# Tests for the ring builder

End-to-end checks of `index.html` in headless Chromium with the real iJewel SDK and configurator (needs internet).

```
pip install pytest playwright
python -m playwright install chromium
python -m pytest tests -q
```

By default the tests serve this folder locally. To test the live page instead:

```
TDO_BASE_URL=https://kkyrylin005.github.io/tdo-ring-builder/ python -m pytest tests -q
```

- `test_smoke.py` - the builder opens with the expected steps and no script errors
- `test_regressions.py` - bugs fixed on 2026-11-15: unsafe `?pave=`, broken `?state=` links, dead controls when loading fails, focus after "Change", viewer controls visible to screen readers
- `test_layout.py` - no sideways scrolling at 320/375/390 px, the step stays in view after Next on a phone, fast band switching keeps the UI in sync
