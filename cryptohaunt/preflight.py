"""Provider-free checks for the registered H2 campaign retry edge."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from .gate import load_manifest, validate_manifest


def assess(root: Path, manifest: dict) -> dict:
    """Assess static readiness without contacting a model provider."""
    errors = validate_manifest(manifest)
    required = [
        "protocol/design-manifest.json",
        "protocol/canary-registry.json",
        "scripts/cryptohaunt",
    ]
    missing = [rel for rel in required if not (root / rel).is_file()]
    errors.extend(f"missing registered artifact: {rel}" for rel in missing)
    integrity_path = root / "protocol/preflight-integrity.json"
    if not integrity_path.is_file():
        errors.append("missing registered artifact: protocol/preflight-integrity.json")
        expected_hashes = {}
    else:
        expected_hashes = json.loads(integrity_path.read_text()).get("artifacts", {})
        for rel in required:
            expected = expected_hashes.get(rel)
            if expected is None:
                errors.append(f"missing declared hash: {rel}")
                continue
            if (root / rel).is_file():
                observed = hashlib.sha256((root / rel).read_bytes()).hexdigest()
                if observed != expected:
                    errors.append(f"hash mismatch: {rel} expected={expected} observed={observed}")
    authorization_open = manifest.get("safety_boundary", {}).get("live_model_campaign_authorized") is True
    if authorization_open:
        return {
            "status": "REFUSED_UNSAFE_MANIFEST",
            "ready": False,
            "authorization_open": True,
            "provider_exclusive_required": True,
            "provider_exclusive_observed": False,
            "static_checks_pass": False,
            "errors": errors,
        }
    return {
        "status": "BLOCKED_EXTERNAL",
        "ready": False,
        "authorization_open": False,
        "provider_exclusive_required": True,
        "provider_exclusive_observed": False,
        "static_checks_pass": not errors,
        "errors": errors,
    }


def run(manifest_path: Path) -> int:
    root = manifest_path.resolve().parents[1]
    result = assess(root, load_manifest(manifest_path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["static_checks_pass"] else 1
