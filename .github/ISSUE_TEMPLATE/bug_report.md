---
name: Bug Report
about: Report a bug to help us improve
title: "[BUG] "
labels: bug
assignees: ''

---

## Description

A clear and concise description of the bug.

## Steps to Reproduce

1. First step
2. Second step
3. ...

## Expected Behavior

What should happen?

## Actual Behavior

What actually happens?

## Screenshots

If applicable, add screenshots to help explain the problem.

## Environment

- **OS**: Windows 10 / Windows 11 / macOS 12+ / Ubuntu 20.04+ / Other
- **App Version**: 0.1.0 (or commit SHA if building from source)
- **Python Version**: 3.10 / 3.11 / 3.12 / Other (run `python3 --version`)
- **GPU**: Yes / No (if yes: NVIDIA / AMD / Other)
- **CUDA Version**: 11.8 / 12.0 / N/A (run `nvcc --version`)

## Error Messages

Paste any error messages from:
1. App UI
2. Terminal/Console
3. Browser DevTools (F12 → Console tab)

```
[Paste error messages here]
```

## Python Environment

```bash
# Run these commands and paste output:
python3 --version
pip list | grep -E "(torch|whisper|requests|fastapi)"
```

## Additional Context

Any other context about the problem?

## Checklist

- [ ] I have checked existing issues and documentation
- [ ] I can reproduce this bug consistently
- [ ] I have provided all requested environment information
- [ ] I have provided error messages and logs
