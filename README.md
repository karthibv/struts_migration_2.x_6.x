# Struts Migration - From version 2.x to 6.x
Migrate from struts 2.5.33 to Struts 6.4.0

This python tool is based on https://cwiki.apache.org/confluence/display/WW/Struts+2.5+to+6.0.0+migration.

### Alternate Stuts Migration Utility option 
Use Open rewrite for struts migration: you can refer : https://docs.openrewrite.org/recipes/java/struts/migrate6/migratestruts6

## Migration Tool

```bash
python struts_migration.py --config /path/to/config.yaml --project-dir /path/to/project
```

### Key features of the configuration-driven approach:

1. Externalized Configuration:
   - All paths and settings in YAML config
   - Easy to modify without changing code
   - Environment-specific configurations

2. Flexible Path Management:
   - Configurable source directories
   - Custom inclusion/exclusion patterns
   - Backup directory configuration

3. Customizable Processing:
   - Batch size control
   - Parallel processing configuration
   - Logging settings

4. Enhanced Safety:
   - Path validation
   - Configurable backup
   - Rollback capability

5. Logging Configuration:
   - Log rotation
   - Configurable formats
   - Multiple output targets

To customize for your project:

1. Modify the `config.yaml`:
   - Update paths for your project structure
   - Adjust include/exclude patterns
   - Configure backup settings
   - Set logging preferences

2. Run with specific paths:
```bash

python struts_migration.py \
  --config /path/to/config.yaml \
  --project-dir /path/to/your/project
```



