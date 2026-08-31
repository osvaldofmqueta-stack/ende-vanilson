---
name: Local database fallback
description: Local Windows installs may not have Replit's managed PostgreSQL environment variables.
---

The application should use the managed PostgreSQL connection when it is available, but allow a local installation without PostgreSQL variables to run on SQLite with an explicit warning.

**Why:** A downloaded Windows copy does not inherit Replit's runtime-managed `DATABASE_URL` or `PG*` variables, so requiring them prevents setup from reaching the migration step.

**How to apply:** Keep PostgreSQL as the Replit and deployment database; treat SQLite only as the documented local-development fallback and do not present it as the production database.