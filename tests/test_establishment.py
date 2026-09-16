import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.probe import Call, DerailState
from cryptohaunt.runner import establishment, replay


class TestEstablishmentOnly(unittest.TestCase):
    def test_establishment_writes_induction_only_and_replays_gate(self):
        state = DerailState(
            messages=[{"role": "user", "content": "rule"}],
            turns_run=1,
            first_break_turn=None,
            obeyed=[True],
            calls=[Call("derail", "turn1", "rule", "bCjcus", None, 0.01)],
        )
        with TemporaryDirectory() as tmp:
            tape = Path(tmp) / "establishment.jsonl"
            args = SimpleNamespace(
                model="tiny", provider="ollama", rule="abcase", seed_word="Abacus",
                turns=1, reps=1, temperature=0.7, seed=19, timeout=1.0,
                out=str(tape), resume=None,
            )
            with patch("cryptohaunt.runner.derail", return_value=state):
                result = establishment(args)

            rows = [json.loads(line) for line in tape.read_text().splitlines()]
            self.assertEqual(rows[0]["kind"], "header")
            self.assertTrue(rows[0]["establishment_only"])
            self.assertEqual([row["kind"] for row in rows[1:]], ["status", "call"])
            self.assertEqual(result, "ESTABLISHED")
            self.assertEqual(replay(str(tape)), "ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
