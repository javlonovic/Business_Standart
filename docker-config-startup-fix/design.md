# Docker Configuration Startup Fix - Bugfix Design

## Overview

The Business Standart platform fails to start in Docker due to environment variable validation errors in the Settings class. The application encounters `json.decoder.JSONDecodeError` when attempting to parse the CORS_ORIGINS field during Settings instantiation. This prevents the FastAPI application from starting, blocks database migrations, and renders the entire platform inaccessible in Docker environments.

The fix involves correcting the pydantic-settings configuration to properly handle environment variable parsing, specifically addressing the CORS_ORIGINS field validation and ensuring all required environment variables are correctly loaded during application startup.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when Settings class is instantiated from environment variables in Docker container context
- **Property (P)**: The desired behavior - Settings should successfully parse all environment variables without JSON decoding errors
- **Preservation**: Existing configuration loading behavior for already-working environments must remain unchanged
- **Settings**: The pydantic BaseSettings class in `backend/app/core/config.py` that loads and validates configuration from environment variables
- **CORS_ORIGINS**: A List[str] field that accepts comma-separated origin URLs for Cross-Origin Resource Sharing configuration
- **field_validator**: Pydantic decorator used to transform and validate field values during model instantiation

## Bug Details

### Fault Condition

The bug manifests when the pydantic-settings library attempts to instantiate the Settings class from environment variables during Docker container startup. The Settings class has a CORS_ORIGINS field typed as `List[str]`, and pydantic-settings is attempting to parse it as JSON before the custom `field_validator` can process it as a comma-separated string.

**Formal Specification:**
```
FUNCTION isBugCondition(context)
  INPUT: context of type ApplicationStartupContext
  OUTPUT: boolean
  
  RETURN context.environment == "docker"
         AND context.loadingSettings == true
         AND existsEnvVar("CORS_ORIGINS")
         AND envVarValue("CORS_ORIGINS") IS comma_separated_string
         AND NOT envVarValue("CORS_ORIGINS") IS valid_json_array
         AND pydanticSettings.attempts_json_parse_before_validator("CORS_ORIGINS")
END FUNCTION
```

### Examples

- **Example 1**: Starting backend container with `CORS_ORIGINS=http://localhost:3000,http://localhost:8080` results in `json.decoder.JSONDecodeError: Expecting value` because pydantic-settings tries to parse the string as JSON array before the validator runs
  - **Expected**: Settings successfully parses the comma-separated string into `["http://localhost:3000", "http://localhost:8080"]`
  - **Actual**: Application crashes during startup with JSON parsing error

- **Example 2**: Running `docker-compose up` with all services causes backend container to fail initialization, logs show `pydantic_settings.exceptions.SettingsError: error parsing value for field "CORS_ORIGINS"`
  - **Expected**: All containers start successfully and backend responds to health checks
  - **Actual**: Backend container is "Up" but application is not running, health check returns connection refused

- **Example 3**: Attempting to run migrations via `docker-compose exec backend alembic upgrade head` fails because `alembic/env.py` imports settings and Settings instantiation fails
  - **Expected**: Migrations run successfully and database schema is created
  - **Actual**: Migration command fails with Settings validation error before any SQL is executed

- **Edge Case**: If CORS_ORIGINS is set as empty string or not provided, Settings instantiation might succeed with default empty list, but actual configuration would still be incorrect for the application's needs

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- When CORS_ORIGINS is provided as a valid JSON array string (e.g., `'["http://localhost:3000"]'`), it must continue to be parsed correctly
- When running in non-Docker environments with properly formatted environment variables, Settings must continue to load without any changes
- All other environment variables (DATABASE_URL, REDIS_URL, SECRET_KEY, etc.) must continue to be loaded exactly as before
- The field_validator logic for parse_cors_origins must continue to split comma-separated strings correctly
- Application behavior after successful Settings instantiation must remain unchanged

**Scope:**
All configuration loading scenarios that currently work correctly should be completely unaffected by this fix. This includes:
- Production deployments with properly configured environment variables
- Local development without Docker where .env file is read directly
- Any environment where CORS_ORIGINS is already in a format that works
- All non-CORS configuration fields

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Pydantic-settings JSON Parsing Behavior**: Pydantic-settings v2.x automatically attempts to parse string values as JSON for fields typed as `List[str]` or other collection types BEFORE custom validators run. When it encounters `http://localhost:3000,http://localhost:8080`, it tries to parse this as JSON, which fails because it's not valid JSON syntax (missing brackets and quotes).

2. **Validator Mode Timing**: The `field_validator` is set to `mode='before'` which should run before validation, but pydantic-settings may be attempting JSON deserialization at the environment variable loading stage, which happens even before the validator chain begins.

3. **Missing env_parse Config**: The Settings.Config class may need explicit configuration to tell pydantic-settings NOT to attempt JSON parsing for specific fields, or to use a different parsing strategy for list-like fields.

4. **Docker Environment Variable Escaping**: Docker and docker-compose may be handling the CORS_ORIGINS string differently than direct shell environments, potentially adding or removing quotes in ways that cause pydantic-settings to misinterpret the value type.

## Correctness Properties

Property 1: Fault Condition - Settings Instantiation with Comma-Separated CORS_ORIGINS

_For any_ environment configuration where CORS_ORIGINS is set as a comma-separated string (e.g., "http://localhost:3000,http://localhost:8080") in a Docker container context, the fixed Settings class SHALL successfully parse the value into a List[str] without raising json.decoder.JSONDecodeError or SettingsError, and the application SHALL start successfully with the parsed origins available in settings.CORS_ORIGINS.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Preservation - Existing Configuration Loading

_For any_ environment configuration that currently loads Settings successfully (non-Docker environments, JSON array format CORS_ORIGINS, or any other working configuration), the fixed Settings class SHALL produce exactly the same parsed configuration values as before, preserving all existing functionality and not introducing any breaking changes to configuration loading behavior.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct (pydantic-settings JSON parsing before validator):

**File**: `backend/app/core/config.py`

**Function**: `Settings` class and `parse_cors_origins` validator

**Specific Changes**:
1. **Add json_schema_extra to CORS_ORIGINS field**: Explicitly configure the field to prevent automatic JSON parsing
   - Add `Field` annotation with `json_schema_extra` to control parsing behavior
   - Alternative: Use `env_parse_none_str` in Config class

2. **Ensure validator runs at correct time**: Verify `mode='before'` is appropriate
   - May need to adjust to catch the raw string before any pydantic processing
   - Consider using `@model_validator` if field-level validator is insufficient

3. **Add explicit type handling**: Make the validator more robust to handle different input formats
   - Check if input is already a list (from JSON parsing in other envs)
   - Check if input is a string (from comma-separated format)
   - Handle empty string and None cases explicitly

4. **Update Settings.Config**: Add pydantic-settings specific configuration
   - Set `json_loads` or parsing strategy if needed
   - Consider `env_nested_delimiter` settings
   - May need `extra='allow'` or other parsing directives

5. **Add validation logging**: Include debug logging in validator to help diagnose future issues
   - Log the type and value received by validator
   - Log the parsed result
   - This aids troubleshooting without requiring container rebuilds

### Specific Implementation Approach

```python
from pydantic import field_validator, Field
from typing import List, Union

class Settings(BaseSettings):
    # Other fields...
    
    # Option A: Use Field with json_schema_extra
    CORS_ORIGINS: List[str] = Field(
        default=[],
        description="Allowed CORS origins as comma-separated string or JSON array"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # Handle if already parsed as list (from JSON or other sources)
        if isinstance(v, list):
            return v
        
        # Handle string input (comma-separated)
        if isinstance(v, str):
            # Empty string case
            if not v or v.strip() == '':
                return []
            
            # Try JSON parsing first (for backwards compatibility)
            if v.strip().startswith('['):
                try:
                    import json
                    return json.loads(v)
                except Exception:
                    pass
            
            # Parse as comma-separated
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        
        # Fallback for unexpected types
        return []
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Add if needed: json_loads = custom_json_loader
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code by attempting to start the application in Docker, then verify the fix works correctly and preserves existing behavior across multiple environment configurations.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Attempt to start the backend container with various CORS_ORIGINS configurations and capture the exact error messages. Run these tests on the UNFIXED code to observe failures and understand the precise nature of the JSON parsing error.

**Test Cases**:
1. **Comma-Separated CORS Test**: Set `CORS_ORIGINS=http://localhost:3000,http://localhost:8080` and start container (will fail on unfixed code)
2. **Single Origin Test**: Set `CORS_ORIGINS=http://localhost:3000` and start container (may fail on unfixed code)
3. **Empty CORS Test**: Set `CORS_ORIGINS=` (empty string) and start container (may succeed but with wrong config)
4. **JSON Array Format Test**: Set `CORS_ORIGINS='["http://localhost:3000"]'` and start container (may succeed, testing preservation)

**Expected Counterexamples**:
- Backend container logs show `json.decoder.JSONDecodeError: Expecting value at line 1 column 1` when parsing CORS_ORIGINS
- Application fails to start before reaching uvicorn server initialization
- Possible causes: pydantic-settings JSON parsing before validator, Docker env var escaping issues, validator timing problems

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds (Docker startup with comma-separated CORS_ORIGINS), the fixed Settings class produces the expected behavior.

**Pseudocode:**
```
FOR ALL config WHERE isBugCondition(config) DO
  result := Settings.instantiate_from_env(config)
  ASSERT result.CORS_ORIGINS IS List[str]
  ASSERT result.CORS_ORIGINS == expected_parsed_list
  ASSERT application_starts_successfully()
  ASSERT health_check_returns_200()
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (working configurations in other environments), the fixed Settings class produces the same result as the original Settings class.

**Pseudocode:**
```
FOR ALL config WHERE NOT isBugCondition(config) DO
  ASSERT Settings_fixed.instantiate(config) == Settings_original.instantiate(config)
  ASSERT application_behavior_unchanged(config)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across different environment variable combinations
- It catches edge cases in configuration parsing that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy configuration scenarios

**Test Plan**: Document current behavior with various environment configurations on UNFIXED code (if possible to test outside Docker), then write property-based tests capturing that behavior.

**Test Cases**:
1. **JSON Array Format Preservation**: Verify that CORS_ORIGINS as `'["http://localhost:3000"]'` continues to parse correctly after fix
2. **Other Environment Variables Preservation**: Verify DATABASE_URL, REDIS_URL, and all other fields load identically before and after fix
3. **Non-Docker Environment Preservation**: Verify Settings loads correctly in local development without Docker
4. **Empty/Missing CORS Preservation**: Verify that missing CORS_ORIGINS still defaults to empty list

### Unit Tests

- Test Settings instantiation with comma-separated CORS_ORIGINS in Docker-like environment
- Test Settings instantiation with JSON array format CORS_ORIGINS
- Test Settings instantiation with empty CORS_ORIGINS
- Test Settings instantiation with single origin (no comma)
- Test that all required fields are validated correctly
- Test field_validator behavior in isolation with different input types

### Property-Based Tests

- Generate random comma-separated origin lists and verify they parse correctly into List[str]
- Generate random combinations of all environment variables and verify Settings instantiates without errors
- Generate edge cases (empty strings, whitespace, special characters) and verify robust handling
- Test that for any valid configuration, Settings always produces consistent results across multiple instantiations

### Integration Tests

- Test full Docker startup flow with test-local.sh script and verify no errors
- Test that migrations run successfully after Settings fix
- Test that health check endpoint responds correctly after container startup
- Test that FastAPI application serves requests correctly with fixed CORS configuration
- Test Celery worker and beat services start correctly with shared Settings
