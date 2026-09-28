# Contributing

`docs/proposal.md` is the source of truth. Schemas and examples must follow it, never the other way round.

## Changing an extension

1. Edit the definition in `docs/proposal.md` (attribute table in Tech Lab format: Attribute · Type · Definition).
2. Update the matching schema in `schemas/`.
3. Update both example sets: `examples/target/` (first-class attributes) and `examples/transition/` (same structure under `ext`).
4. Run the validator:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   .venv/bin/python scripts/validate.py
   ```

5. Add a line to `CHANGELOG.md` and open a pull request. CI runs the same validation.

## Conventions

- Attribute names are short, lowercase, no separators (OpenRTB style: `loopdur`, `crapproval`).
- New value lists reserve `500+` for exchange-specific values.
- Transition paths use identical names under `ext`, so only the path changes on adoption:

  | Target | Transition |
  | --- | --- |
  | `imp.playout` | `imp.ext.playout` |
  | `imp.crapproval` | `imp.ext.crapproval` |
  | `dooh.screen` | `dooh.ext.screen` |
  | `imp.pmp.deals[].billing` | `imp.pmp.deals[].ext.billing` |
  | `bid.billing` | `bid.ext.billing` |

- Open questions go into GitHub issues using the *Open question* template.
