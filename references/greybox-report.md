# Greybox Report Contract

Create `greybox-report.json` in the game project before art, listing, or upload work. Use ordinary player input, not debug hooks. Test the smallest plain-shape loop first, then repeat the same checks against the final build.

```json
{
  "schemaVersion": 1,
  "prototype": {
    "start": { "passed": true, "observation": "Ordinary start input entered gameplay." },
    "agency": { "passed": true, "normalInput": "Exact action", "controlCondition": "Zero or opposite input", "observation": "Concrete difference in outcome." },
    "restart": { "passed": true, "observation": "Collision or completion reached a stable restart and a second playable run." }
  },
  "final": {
    "start": { "passed": true, "observation": "Ordinary start input entered gameplay." },
    "agency": { "passed": true, "normalInput": "Exact action", "controlCondition": "Zero or opposite input", "observation": "Concrete difference in outcome." },
    "restart": { "passed": true, "observation": "Collision or completion reached a stable restart and a second playable run." }
  }
}
```

Each observation must describe visible behavior. If a prototype check fails, fix the player verb and retry once. After two failed attempts, simplify the mechanic and rerun the checks. Do not start assets or listing work while the prototype section is missing or failing. Do not upload while either section is missing or failing.
