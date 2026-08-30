---
name: Replit workflow ports
description: Port behavior to account for when configuring Django web previews in this project
---

Use an explicit `:5000` in the Replit webview workflow command. In this environment, `${PORT}` was passed through unexpanded, causing Django to reject `0.0.0.0:`; webview workflows require port 5000.

**Why:** The first workflow start failed before the server could bind because the workflow shell did not provide the expected `PORT` expansion.

**How to apply:** Keep the Django workflow bound to `0.0.0.0:5000` with `waitForPort: 5000`; do not assume `${PORT}` expands in workflow commands.