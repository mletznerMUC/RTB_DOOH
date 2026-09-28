# RTB_DOOH – OpenRTB DOOH Extensions for the Ströer SSP

Proposal to align the Ströer SSP *DSP Integration API 1.0* with the DOOH building blocks of [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md), and to extend the standard where it has DOOH gaps, most importantly a **`Billing` object** on the Deal that distinguishes standard, direct and DSP-direct settlement.

📄 **Full proposal:** [docs/proposal.md](docs/proposal.md)

## At a glance

**Alignment (Ströer → OpenRTB 2.6, no change to the standard)**

| ID | Change |
| --- | --- |
| A1 | Send `BidRequest.dooh` instead of `site`/`app` |
| A2 | Introduce `imp.qty`; deprecate `imp.ext.totalaud` for DOOH → `qty.multiplier` |
| A3 | Populate `imp.dt` with the scheduled play time |
| A4 | Add `device.devicetype = 8` (out-of-home) |
| A5 | Support `deal.guar` and `deal.wadomain` |
| A6 | Support `bid.burl`, fired after proof of play |

**Extensions (proposed to IAB Tech Lab)**

| ID | Where | What | Schema |
| --- | --- | --- | --- |
| E1 | `Imp.playout` | Loop, slot, share of voice, playout window, screens | [playout](schemas/playout.schema.json) |
| E2 | `DOOH.screen` | Orientation, diagonal, indoor/outdoor, motion, audio | [screen](schemas/screen.schema.json) |
| E3 | `Imp` / `Deal` `.crapproval` | Creative approval by media owner | [crapproval](schemas/crapproval.schema.json) |
| E4 | Macros | `${PLAY_COUNT}`, `${PLAY_TS}`, `${QTY_MULTIPLIER}`, `${BILLING_MODEL}` | checked in validator |
| E5 | `Deal.billing` | Settlement model: 1 standard, 2 direct, 3 dsp_direct | [billing](schemas/billing.schema.json) |
| E6 | `Bid.billing` | Bidder echo of `model` + `ioref` | [bid-billing](schemas/bid-billing.schema.json) |

Until adoption, the extensions run under `ext` with identical names (see [CONTRIBUTING.md](CONTRIBUTING.md#conventions)).

## Repository layout

```
docs/proposal.md          Source of truth: gap analysis, A1–A6, E1–E6, open questions
schemas/                  JSON Schema (2020-12) for each extension + DOOH request/response profiles
examples/target/          Payloads with extensions as first-class attributes
examples/transition/      Same payloads with extensions under ext (what Ströer would send today)
scripts/validate.py       Schema validation + cross-field rules
.github/                  CI workflow and issue templates
```

The request/response schemas are **profiles**, not full OpenRTB 2.6 schemas: they validate the DOOH-relevant parts only.

## Validate

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate.py
```

Besides schema validation, the script checks rules JSON Schema cannot express: `imp.dt == playout.dtstart`, `dtend > dtstart`, `bid.billing.model == deal.billing.model`, required billing echo on direct / DSP-direct deals, and that `burl` only uses known macros.

## Open questions

Tracked in [§7 of the proposal](docs/proposal.md#7-open-questions--next-steps); file new ones as GitHub issues.

## Sources

- [Ströer SSP – DSP Integration API 1.0](https://specs.myadscale.de/dsp-adapter/external/1.0.html#top)
- [IAB Tech Lab OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md)
- [openrtb2.x Issue #49](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/issues/49)
