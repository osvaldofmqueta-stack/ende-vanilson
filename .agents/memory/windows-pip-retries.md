---
name: Windows dependency downloads
description: Network behavior to account for when installing this project's Python dependencies on Windows.
---

The Windows installer should retry pip downloads with a generous timeout because a transient `ConnectionResetError 10054` can interrupt package installation even when Python and the dependency versions are compatible.

**Why:** The remote host can forcibly close an HTTPS connection during a package download; treating the first disconnect as a permanent setup failure creates a misleading installation error.

**How to apply:** Keep retry and timeout behavior in the installer itself, always synchronize the full requirements file, and verify the Django import before continuing.