"""Provider-free checks for the registered H2 campaign retry edge."""
from __future__ import annotations

import json
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
