import os
import yaml
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
import shutil
import sys
from datetime import datetime


@dataclass
class MigrationContext:
    """Context object holding the current migration state and configuration"""
    config: Dict[str, Any]
    logger: logging.Logger
    base_dir: Path
    backup_dir: Path

class ConfigurationManager:
    """Manages configuration loading and validation"""
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            sys.exit(1)

    def _validate_config(self):
        """Validate configuration structure and required fields"""
        required_sections = ['paths', 'files', 'patterns', 'migration', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")

    def update_paths(self, base_dir: str):
        """Update paths based on provided base directory"""
        self.config['paths']['base_dir'] = base_dir
        for key, path in self.config['paths'].items():
            if key != 'base_dir':
                self.config['paths'][key] = os.path.join(base_dir, path)

class LoggingManager:
    """Manages logging configuration and setup"""
    @staticmethod
    def setup_logging(config: Dict[str, Any]) -> logging.Logger:
        """Configure and return logger based on configuration"""
        log_config = config['logging']
        log_file = log_config['file']      
        logger = logging.getLogger('StrutsMigration')
        logger.setLevel(getattr(logging, log_config['level']))

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=parse_size(log_config['max_size']),
            backupCount=log_config['backup_count']
        )
        file_handler.setFormatter(logging.Formatter(log_config['format']))
       
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_config['format']))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

class PathManager:
    """Manages path operations and validations"""
    def __init__(self, context: MigrationContext):
        self.context = context

    def validate_paths(self):
         """Validate existence of required paths"""
        required_paths = [
            self.context.base_dir,
            self.context.base_dir / self.context.config['files']['pom'],
            self.context.base_dir / self.context.config['files']['struts_config']
        ]

        for path in required_paths:
            if not path.exists():
                raise ValueError(f"Required path does not exist: {path}")

    def create_backup_directory(self):
        """Create backup directory if enabled"""
        if self.context.config['migration']['backup_enabled']:
            self.context.backup_dir.mkdir(parents=True, exist_ok=True)


class FileProcessor:
    """Handles file processing and migration"""
    def __init__(self, context: MigrationContext):
        self.context = context

    def process_files(self):
        """Process files according to configuration"""
        patterns = self.context.config['patterns']
        files_to_process = self._gather_files(patterns['include'], patterns['exclude'])      
        batch_size = self.context.config['migration']['batch_size']
        num_threads = self.context.config['migration']['parallel_threads']

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(0, len(files_to_process), batch_size):
                batch = files_to_process[i:i + batch_size]
                futures = [executor.submit(self._process_file, file) for file in batch]
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        self.context.logger.error(f"Error processing file: {str(e)}")

    def _gather_files(self, include_patterns, exclude_patterns):
        """Gather files based on include/exclude patterns"""
        files = []
        for pattern in include_patterns:
            files.extend(self.context.base_dir.glob(pattern))
       

        # Apply exclusion patterns
        for pattern in exclude_patterns:
            files = [f for f in files if not f.match(pattern)]
            
        return files

    def _process_file(self, file_path: Path):
        """Process individual file based on type"""
        try:
            if file_path.suffix == '.java':
                self._process_java_file(file_path)
            elif file_path.suffix == '.xml':
                self._process_xml_file(file_path)
            elif file_path.suffix == '.jsp':
                self._process_jsp_file(file_path)
        except Exception as e:
            self.context.logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _process_java_file(self, file_path: Path):
        """Process Java file"""
        # Implementation from previous script
        pass


    def _process_xml_file(self, file_path: Path):
        """Process XML file"""
        # Implementation from previous script
        pass


    def _process_jsp_file(self, file_path: Path):
        """Process JSP file"""
        # Implementation from previous script
        pass


class MigrationManager:
    """Manages the overall migration process"""
    def __init__(self, config_file: str, base_dir: str):
        self.config_manager = ConfigurationManager(config_file)
        self.config_manager.update_paths(base_dir)
       
        self.context = MigrationContext(
            config=self.config_manager.config,
            logger=LoggingManager.setup_logging(self.config_manager.config),
            base_dir=Path(base_dir),
            backup_dir=Path(base_dir) / self.config_manager.config['paths']['backup_dir']
        )
        self.path_manager = PathManager(self.context)
        self.file_processor = FileProcessor(self.context)


    def execute_migration(self):
        """Execute the migration process"""
        try:
            # Validate environment
            self.path_manager.validate_paths()
            
            # Create backup if enabled
            if self.context.config['migration']['backup_enabled']:
                self.path_manager.create_backup_directory()
                

            # Process files
            self.file_processor.process_files()
            

            # Generate report
            self._generate_report()

            
        except Exception as e:
            self.context.logger.error(f"Migration failed: {str(e)}")
            if self.context.config['migration']['rollback_enabled']:
                self._rollback()
            raise


    def _generate_report(self):
        """Generate migration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project': self.context.config['project'],
            'status': 'completed',
            'details': {
                'files_processed': 0,  # Add actual counts
                'errors': []  # Add actual errors
            }
        }
       
        report_file = self.context.base_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _rollback(self):
        """Rollback changes if enabled"""
        if self.context.backup_dir.exists():
            shutil.rmtree(self.context.base_dir)
            shutil.copytree(self.context.backup_dir, self.context.base_dir)
            self.context.logger.info("Rollback completed")


def parse_size(size_str: str) -> int:
    """Parse size string (e.g., '10MB') to bytes"""
    units = {'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
    number = int(''.join(filter(str.isdigit, size_str)))
    unit = ''.join(filter(str.isalpha, size_str.upper()))
    return number * units[unit]


def main():
    parser = argparse.ArgumentParser(description='Struts Migration Utility')
    parser.add_argument('--config', required=True, help='Path to configuration file')
    parser.add_argument('--project-dir', required=True, help='Path to project directory')
    args = parser.parse_args()


    try:
        migration_manager = MigrationManager(args.config, args.project_dir)
        migration_manager.execute_migration()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
