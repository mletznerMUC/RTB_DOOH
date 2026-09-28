#!/usr/bin/env python3
"""Validate example payloads against the DOOH extension schemas.

Schema validation covers structure and value lists. The cross-field rules
from the proposal that JSON Schema cannot express are checked in code:

- imp.dt should equal playout.dtstart; dtend must be after dtstart (E1)
- bid.billing.model must equal deal.billing.model of bid.dealid (E6)
- burl may only use known macros (Ströer 1.0 + E4)
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"

KNOWN_MACROS = {
    "AUCTION_PRICE", "AUCTION_PRICE:ENC", "AUCTION_ID", "AUCTION_BID_ID",
    "AUCTION_IMP_ID", "AUCTION_LOSS",
    "PLAY_COUNT", "PLAY_TS", "QTY_MULTIPLIER", "BILLING_MODEL",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def registry():
    resources = []
    for p in SCHEMAS.glob("*.schema.json"):
        res = Resource.from_contents(load(p))
        resources += [(p.name, res), (res.id(), res)]
    return Registry().with_resources(resources)


def ext_or(obj, key):
    """Return a proposal attribute from its first-class or ext location."""
    return obj.get(key, obj.get("ext", {}).get(key))


def describe(error):
    if error.validator == "not" and error.json_path == "$":
        return "$: must not contain site or app alongside dooh (OpenRTB 2.6 §3.2.1)"
    return f"{error.json_path}: {error.message}"


def check_request(req):
    errors, deals = [], {}
    for imp in req.get("imp", []):
        playout = ext_or(imp, "playout")
        if playout:
            start, end = playout.get("dtstart"), playout.get("dtend")
            if start is not None and "dt" in imp and imp["dt"] != start:
                errors.append(f"imp {imp['id']}: dt != playout.dtstart")
            if start is not None and end is not None and end <= start:
                errors.append(f"imp {imp['id']}: playout.dtend must be after dtstart")
        for deal in imp.get("pmp", {}).get("deals", []):
            deals[deal["id"]] = (ext_or(deal, "billing") or {}).get("model", 1)
    return errors, deals


def check_response(resp, deals):
    errors = []
    for seatbid in resp.get("seatbid", []):
        for bid in seatbid["bid"]:
            for macro in re.findall(r"\$\{([^}]+)\}", bid.get("burl", "")):
                if macro not in KNOWN_MACROS:
                    errors.append(f"bid {bid['id']}: unknown macro ${{{macro}}} in burl")
            billing = ext_or(bid, "billing")
            dealid = bid.get("dealid")
            if dealid in deals:
                expected = deals[dealid]
                got = billing["model"] if billing else 1
                if got != expected:
                    errors.append(f"bid {bid['id']}: billing model mismatch ({got} != deal {expected})")
                if expected in (2, 3) and not billing:
                    errors.append(f"bid {bid['id']}: deal {dealid} requires billing echo")
    return errors


def main():
    reg = registry()
    validators = {
        kind: Draft202012Validator(load(SCHEMAS / f"{kind}.schema.json"), registry=reg)
        for kind in ("bid-request", "bid-response")
    }
    failed = False
    for folder in sorted(p for p in EXAMPLES.iterdir() if p.is_dir()):
        req_path, resp_path = folder / "bid-request.json", folder / "bid-response.json"
        req, resp = load(req_path), load(resp_path)
        problems = [f"{req_path.name}: {describe(e)}" for e in validators["bid-request"].iter_errors(req)]
        problems += [f"{resp_path.name}: {describe(e)}" for e in validators["bid-response"].iter_errors(resp)]
        rule_errors, deals = check_request(req)
        problems += rule_errors + check_response(resp, deals)
        status = "FAIL" if problems else "ok"
        print(f"[{status}] examples/{folder.name}")
        for p in problems:
            print(f"    - {p}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
