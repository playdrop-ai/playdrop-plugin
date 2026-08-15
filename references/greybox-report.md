# Optional Greybox Evidence

Use `greybox-report.json` when a new or risky mechanic benefits from an explicit before-and-after check. It is working evidence, not an upload requirement, and it does not control when art or listing work may begin. Use ordinary player input, not debug hooks.

```json
{
  "schemaVersion": 1,
  "prototype": {
    "start": { "passed": true, "observation": "Ordinary start input entered gameplay." },
    "agency": {
      "passed": true,
      "normalInput": "Exact action",
      "controlCondition": "Zero or opposite input",
      "observation": "Concrete difference in outcome."
    },
    "restart": {
      "passed": true,
      "observation": "Collision or completion reached a stable restart and a second playable run."
    }
  },
  "final": {
    "start": { "passed": true, "observation": "Ordinary start input entered gameplay." },
    "agency": {
      "passed": true,
      "normalInput": "Exact action",
      "controlCondition": "Zero or opposite input",
      "observation": "Concrete difference in outcome."
    },
    "restart": {
      "passed": true,
      "observation": "Collision or completion reached a stable restart and a second playable run."
    }
  }
}
```

Each observation should describe visible behavior. Use whichever sections help the work; the final deterministic tape remains the upload-facing gameplay check.
