---
name: Bootstrap credentials
description: Secure account provisioning behavior for local and Replit setup.
---

Initial account provisioning must never ship a fixed password in source, documentation, installer output, or the login page. New passwords are collected interactively or supplied through environment secrets; existing passwords are not reset by setup.

**Why:** A known administrator password becomes an immediate account takeover risk when the server is reachable beyond the local machine.

**How to apply:** Keep provisioning idempotent, require a password of at least eight characters, and use secret environment variables only for non-interactive automation.