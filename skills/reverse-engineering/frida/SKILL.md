---
name: frida
description: Use Frida for dynamic instrumentation — hook and modify apps at runtime on Android, iOS, and Windows. Use to observe behavior, bypass checks in your own test apps, and analyze runtime logic that static analysis misses.
---

# Frida — Dynamic Instrumentation Toolkit

- Repo: https://github.com/frida/frida (C + Python & JavaScript bindings)
- Purpose: Dynamic analysis and runtime modification.
- Install: `pip install frida-tools` (Python) — verify with `frida --version`.
- Very popular in security research.

## Core commands

```bash
frida-ps -U              # list processes on USB device (Android)
frida-trace -U -f com.example.app -j "*!*password*"
frida -U -f com.example.app -l hook.js
```

## Example hook (JavaScript, Android)

```javascript
Java.perform(function () {
  var String = Java.use('java.lang.String');
  String.equals.implementation = function (other) {
    console.log('[+] equals called: ' + this + ' vs ' + other);
    return this.equals(other);
  };
});
```

## When to use

- Static analysis (Ghidra/radare2) shows *what* the code is; Frida shows
  *what it does at runtime* — values, arguments, return codes.
- Android/iOS app analysis, malware behavior observation, your own apps.

## Begonia kernel use

Frida runs in userspace — use it to instrument Android apps on the
Begonia device (Redmi Note 8 Pro) while the custom kernel runs underneath.
Pair with `adb` + `frida-server` pushed to the device.

## Ethics

- Only instrument apps you own or have permission to analyze.
- Use in a safe environment (VM / test device) for untrusted samples.
- For learning, research, and security purposes only.
