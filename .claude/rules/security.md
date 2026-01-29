# Security Rules

Security guidelines for dbt data transformation projects.

## dbt-Specific Security

### Never Commit

- Database credentials or connection strings
- API keys or tokens
- `.env` files with secrets
- `profiles.yml` with credentials (use env vars)

### Credential Handling

```yaml
# profiles.yml - CORRECT: use environment variables
my_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DBT_DATABASE_PATH') }}"
```

### Source Data Security

- Never expose PII in model names or column descriptions
- Use masking/hashing for sensitive columns in staging
- Document data classification in model YAML

```sql
-- Mask sensitive data in staging
select
    patient_id,
    md5(ssn) as ssn_hash,  -- Hash PII
    left(zip_code, 3) as zip_prefix  -- Partial only
from source
```

## Code Review Checklist

- [ ] No hardcoded credentials
- [ ] profiles.yml uses env vars
- [ ] PII masked/hashed appropriately
- [ ] No sensitive data in logs or descriptions
- [ ] .gitignore excludes credential files
