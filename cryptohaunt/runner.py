"""Tie the phases together, write the tape, read the tape back."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

from . import __version__
from .probe import control, derail, noise, switch
from .probes import Probe, load_probes
from .report import Arm, collect, render, verdict_for
from .rules import RULES


class ConfigError(ValueError):
    pass


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_config(args) -> dict:
    if args.rule not in RULES:
        raise ConfigError(f"unknown rule {args.rule!r}; have {sorted(RULES)}")
    if args.reps > 1 and args.temperature == 0.0 and args.seed is not None:
        raise ConfigError(
            f"--reps {args.reps} at temperature 0 with a fixed seed draws the same "
            "answer every time; that is n=1 wearing an n of "
            f"{args.reps}. Raise --temperature or pass --seed none."
        )
    return {
        "model": args.model,
        "provider": args.provider,
        "temperature": args.temperature,
        "seed": args.seed,
        "timeout": args.timeout,
    }


def run(args) -> str:
    cfg = build_config(args)
    rule = RULES[args.rule]
    probes = load_probes(args.probes)
    families = {p.key: p.family for p in probes}

    out_path = args.out or os.path.join(
        "runs", f"{args.model.replace('/', '_')}_{args.rule}_{int(time.time())}.jsonl"
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    arms: dict[str, list] = {"switch": [], "control": [], "noise": []}
    derail_notes: list[str] = []
    statuses: list[str] = []

    with open(out_path, "w", encoding="utf-8") as tape:
        tape.write(
            json.dumps(
                {
                    "kind": "header",
                    "version": __version__,
                    "started": _stamp(),
                    "model": args.model,
                    "provider": args.provider,
                    "rule": args.rule,
                    "seed_word": args.seed_word,
                    "turns": args.turns,
                    "reps": args.reps,
                    "temperature": args.temperature,
                    "sampling_seed": args.seed,
                    "probes": [p.key for p in probes],
                }
            )
            + "\n"
        )

        for rep in range(1, args.reps + 1):
            rep_cfg = dict(cfg)
            if rep_cfg["seed"] is not None:
                rep_cfg["seed"] = rep_cfg["seed"] + rep

            state = derail(rep_cfg, rule, args.seed_word, args.turns)
            statuses.append(state.status)
            derail_notes.append(
                f"rep{rep}: {state.status}, broke at turn {state.first_break_turn or '-'}, "
                f"obeyed {sum(state.obeyed)}/{len(state.obeyed)}, calls {state.coverage}"
            )
            tape.write(
                json.dumps(
                    {
                        "kind": "status",
                        "rep": rep,
                        "status": state.status,
                        "obeyed": state.obeyed,
                        "first_break_turn": state.first_break_turn,
                    }
                )
                + "\n"
            )
            for call in state.calls:
                tape.write(json.dumps({"kind": "call", "rep": rep, **call.__dict__}) + "\n")

            for arm_name, results in (
                ("switch", switch(rep_cfg, state, probes, rule)),
                ("noise", noise(rep_cfg, state, probes, rule, args.seed_word)),
                ("control", control(rep_cfg, probes, rule)),
            ):
                for call, finding in results:
                    tape.write(
                        json.dumps(
                            {
                                "kind": "graded",
                                "rep": rep,
                                "arm": arm_name,
                                "probe": call.label,
                                "family": families[call.label],
                                **call.__dict__,
                                "finding": finding.as_dict(),
                            }
                        )
                        + "\n"
                    )
                    arms[arm_name].append((call.label, finding))

            if args.verbose:
                print(f"  {derail_notes[-1]}", flush=True)

    text = summarise(
        arms,
        families,
        _overall_status(statuses),
        {
            "model": args.model,
            "provider": args.provider,
            "rule": args.rule,
            "seed_word": args.seed_word,
            "derail_summary": "; ".join(derail_notes),
            "reps": args.reps,
            "temperature": args.temperature,
            "seed": args.seed,
        },
    )
    return f"{text}\n\ntape: {out_path}"


def _overall_status(statuses: list[str]) -> str:
    """A run counts as derailed if ANY repetition derailed.

    Reported as the worst-case word otherwise, so a set of reps in which the
    model never once held the rule cannot present itself as a null result.
    """
    if not statuses:
        return "no-calls"
    if "derailed" in statuses:
        return "derailed"
    for word in ("recovered", "not-established", "no-calls"):
        if word in statuses:
            return word
    return "no-calls"


def summarise(arms: dict, families, status, header) -> str:
    folded = {name: collect(items, families) for name, items in arms.items()}
    empty = Arm(0, 0, 0.0)
    order = list(dict.fromkeys(families.values()))
    verdicts = [
        verdict_for(
            f,
            folded["switch"].get(f, empty),
            folded["control"].get(f, empty),
            folded["noise"].get(f, empty),
            status,
        )
        for f in order
    ]
    return render(verdicts, header)


def replay(path: str) -> str:
    """Re-derive the verdict from a tape, with no network at all."""
    header = None
    families: dict[str, str] = {}
    arms: dict[str, list] = {"switch": [], "control": [], "noise": []}
    derail_by_rep: dict[int, list[bool]] = {}

    from .detect import Finding

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["kind"] == "header":
                header = row
            elif row["kind"] == "graded":
                families[row["probe"]] = row["family"]
                f = row["finding"]
                arms.setdefault(row["arm"], []).append(
                    (row["probe"], Finding(f["detector"], f["value"], f["reason"], f["evidence"]))
                )
            elif row["kind"] == "status":
                derail_by_rep[row["rep"]] = row["status"]

    if header is None:
        raise ConfigError(f"{path} has no header line; is it a cryptohaunt tape?")

    # A replay cannot re-judge whether the rule broke - that is a fact about the
    # derail turns, recorded at run time. Take it from the tape, or refuse.
    status = _overall_status(list(derail_by_rep.values()))
    return summarise(
        arms,
        families,
        status,
        {
            "model": header["model"],
            "provider": header["provider"],
            "rule": header["rule"],
            "seed_word": header["seed_word"],
            "derail_summary": f"replayed from tape ({len(derail_by_rep)} rep(s)): {status}",
            "reps": header["reps"],
            "temperature": header["temperature"],
            "seed": header["sampling_seed"],
        },
    )
