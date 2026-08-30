"""cryptohaunt <run|replay|probes|selftest>"""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .runner import ConfigError, replay, run


def _seed(value: str):
    if value.lower() in ("none", "off", ""):
        return None
    return int(value)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cryptohaunt", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="derail a model, then ask it about something else")
    r.add_argument("--model", required=True, help="e.g. qwen2.5:3b or moonshotai/kimi-k2-instruct")
    r.add_argument("--provider", default="ollama", choices=["ollama", "groq", "openai"])
    r.add_argument("--rule", default="zy", help="zy | o2cyrillic")
    r.add_argument("--seed-word", default="mozerov", dest="seed_word")
    r.add_argument("--turns", type=int, default=10, help="derailment turns before the switch")
    r.add_argument("--reps", type=int, default=1, help="independent repetitions of the whole run")
    r.add_argument("--temperature", type=float, default=0.7)
    r.add_argument("--seed", type=_seed, default=7, help="sampling seed, or 'none'")
    r.add_argument("--timeout", type=float, default=120.0)
    r.add_argument("--probes", default=None, help="JSON file of probes; omit for the shipped set")
    r.add_argument("--out", default=None, help="tape path (default runs/<model>_<rule>_<ts>.jsonl)")
    r.add_argument("-v", "--verbose", action="store_true")

    q = sub.add_parser("replay", help="re-derive a verdict from a tape, offline")
    q.add_argument("tape")

    sub.add_parser("probes", help="print the shipped probe set")
    sub.add_parser("selftest", help="run the detectors against their fixtures, no network")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "run":
            print(run(args))
        elif args.cmd == "replay":
            print(replay(args.tape))
        elif args.cmd == "probes":
            from .probes import DEFAULT_PROBES

            for probe in DEFAULT_PROBES:
                print(f"[{probe.family}] {probe.key} -> {probe.expects}\n    {probe.question}\n")
        elif args.cmd == "selftest":
            import unittest

            loader = unittest.TestLoader().discover("tests", top_level_dir=".")
            result = unittest.TextTestRunner(verbosity=2).run(loader)
            return 0 if result.wasSuccessful() else 1
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
