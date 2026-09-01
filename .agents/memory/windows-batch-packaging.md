---
name: Windows batch packaging
description: Constraints for distributing Windows batch installers from this project
---

Windows batch installers packaged from the Linux workspace must use CRLF line endings before distribution, and interpreter detection must execute a version check rather than trusting `where` or the Microsoft Store execution alias.

**Why:** A Windows installation reproduced the classic symptoms of malformed batch parsing (first characters missing from commands), and the Store alias could be mistaken for a working Python executable.

**How to apply:** Convert distributed `.bat` files to CRLF in the release package and make the installer stop with a clear message unless Python 3.11+ successfully runs a small command.