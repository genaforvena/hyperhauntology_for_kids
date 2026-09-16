"""Tie the phases together, write the tape, read the tape back."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

from . import __version__
from .probe import control, derail, noise, switch
from .probes import Probe, load_probes
from .report import DEFAULT_MDE, Arm, collect, render, verdict_for
from .rules import RULES
from .tape import completed_repetitions, read_tape, validate_resume_header


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

    if args.resume and args.out:
        raise ConfigError("--resume and --out cannot be used together")
    out_path = args.resume or args.out or os.path.join(
        "runs", f"{args.model.replace('/', '_')}_{args.rule}_{int(time.time())}.jsonl"
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    arms: dict[str, list] = {"switch": [], "control": [], "noise": []}
    derail_notes: list[str] = []
    statuses: list[str] = []

    completed: set[int] = set()
    if args.resume:
        tape = read_tape(out_path)
        validate_resume_header(tape.header, args, [p.key for p in probes])
        completed = completed_repetitions(
            tape, [p.key for p in probes], ["switch", "control", "noise"]
        )
        eligible = {
            rep
            for rep in completed
            if any(
                row.get("kind") == "status"
                and row.get("rep") == rep
                and row.get("status") == "derailed"
                for row in tape.rows
            )
        }
        _load_completed_rows(tape.rows, completed, eligible, arms, families, statuses)

    # Line-buffered: a run that is killed, times out or loses the machine keeps
    # every call it already paid for. The default 8KB buffer loses the whole tape
    # on a SIGTERM, which is exactly when a long run is most likely to end.
    mode = "a" if args.resume else "w"
    with open(out_path, mode, encoding="utf-8", buffering=1) as tape:
        if not args.resume:
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
                        "max_mde": args.max_mde,
                        "probes": [p.key for p in probes],
                    }
                )
                + "\n"
            )

        for rep in range(1, args.reps + 1):
            if rep in completed:
                continue
            rep_cfg = dict(cfg)
            if rep_cfg["seed"] is not None:
                rep_cfg["seed"] = rep_cfg["seed"] + rep

            state = derail(rep_cfg, rule, args.seed_word, args.turns)
            statuses.append(state.status)
            derail_notes.append(
                f"rep{rep}: {state.status}, broke at turn {state.first_break_turn or '-'}, "
                f"obeyed {sum(1 for o in state.obeyed if o)}/{len(state.spoken)} spoken, "
                f"{state.mute_turns} mute, calls {state.coverage}"
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
                    if state.status == "derailed":
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
        max_mde=getattr(args, "max_mde", DEFAULT_MDE),
    )
    return f"{text}\n\ntape: {out_path}"


def establishment(args) -> str:
    """Run only the registered induction gate; never spend persistence probes."""
    cfg = build_config(args)
    rule = RULES[args.rule]
    if args.reps != 1:
        raise ConfigError("establishment-only accepts exactly one repetition")
    if args.resume:
        raise ConfigError("establishment-only does not support --resume")
    out_path = args.out or os.path.join(
        "runs", f"{args.model.replace('/', '_')}_{args.rule}_establishment-{int(time.time())}.jsonl"
    )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    state = derail(cfg, rule, args.seed_word, args.turns)
    gate_status = "established" if state.established else state.status
    with open(out_path, "w", encoding="utf-8", buffering=1) as tape:
        tape.write(json.dumps({
            "kind": "header", "version": __version__, "establishment_only": True,
            "started": _stamp(), "model": args.model, "provider": args.provider,
            "rule": args.rule, "seed_word": args.seed_word, "turns": args.turns,
            "reps": 1, "temperature": args.temperature, "sampling_seed": args.seed,
        }) + "\n")
        tape.write(json.dumps({
            "kind": "status", "rep": 1, "status": gate_status,
            "obeyed": state.obeyed, "first_break_turn": state.first_break_turn,
        }) + "\n")
        for call in state.calls:
            tape.write(json.dumps({"kind": "call", "rep": 1, **call.__dict__}) + "\n")
    return "ESTABLISHED" if state.established else gate_status.upper()


def _load_completed_rows(rows, completed, eligible, arms, families, statuses):
    """Load only complete reps; partial rows remain evidence but not findings."""
    from .detect import Finding

    for row in rows:
        if row.get("rep") not in completed:
            continue
        if row.get("kind") == "status":
            statuses.append(row["status"])
        elif row.get("kind") == "graded" and row.get("rep") in eligible:
            f = row["finding"]
            arms[row["arm"]].append(
                (row["probe"], Finding(f["detector"], f["value"], f["reason"], f["evidence"]))
            )


def _overall_status(statuses: list[str]) -> str:
    """A run counts as derailed if ANY repetition derailed.

    Reported as the worst-case word otherwise, so a set of reps in which the
    model never once held the rule cannot present itself as a null result.
    """
    if not statuses:
        return "no-calls"
    if "derailed" in statuses:
        return "derailed"
    for word in ("recovered", "not-established", "truncated", "mute", "no-calls"):
        if word in statuses:
            return word
    return "no-calls"


def summarise(arms: dict, families, status, header, max_mde: float = DEFAULT_MDE) -> str:
    folded = {name: collect(items, families) for name, items in arms.items()}
    empty = Arm(0, 0, 0.0)
    order = list(dict.fromkeys(families.values()))
    per_family: dict[str, int] = {}
    for fam in families.values():
        per_family[fam] = per_family.get(fam, 0) + 1
    verdicts = [
        verdict_for(
            f,
            folded["switch"].get(f, empty),
            folded["control"].get(f, empty),
            folded["noise"].get(f, empty),
            status,
            max_mde=max_mde,
            probes_per_family=per_family.get(f, 0),
        )
        for f in order
    ]
    return render(verdicts, header)


def replay(path: str) -> str:
    """Re-derive the verdict from a tape, with no network at all."""
    tape = read_tape(path)
    header = tape.header
    if header.get("establishment_only"):
        statuses = [row.get("status") for row in tape.rows if row.get("kind") == "status"]
        if len(statuses) != 1:
            raise ConfigError("establishment-only tape must contain exactly one status row")
        status = statuses[0]
        return "ESTABLISHED" if status == "established" else status.upper()
    families: dict[str, str] = {}
    arms: dict[str, list] = {"switch": [], "control": [], "noise": []}
    for row in tape.rows:
        if row.get("kind") == "graded":
            families[row["probe"]] = row["family"]
    probe_keys = list(families)
    complete = completed_repetitions(tape, probe_keys, ["switch", "control", "noise"])
    derail_by_rep: list[str] = []
    eligible = {
        rep
        for rep in complete
        if any(
            row.get("kind") == "status"
            and row.get("rep") == rep
            and row.get("status") == "derailed"
            for row in tape.rows
        )
    }
    _load_completed_rows(tape.rows, complete, eligible, arms, families, derail_by_rep)

    # A replay cannot re-judge whether the rule broke - that is a fact about the
    # derail turns, recorded at run time. Take it from the tape, or refuse.
    status = _overall_status(derail_by_rep)
    return summarise(
        arms,
        families,
        status,
        {
            "model": header["model"],
            "provider": header["provider"],
            "rule": header["rule"],
            "seed_word": header["seed_word"],
            "derail_summary": f"replayed from tape ({len(complete)} complete rep(s)): {status}",
            "reps": header["reps"],
            "temperature": header["temperature"],
            "seed": header["sampling_seed"],
        },
        max_mde=header.get("max_mde", DEFAULT_MDE),
    )
