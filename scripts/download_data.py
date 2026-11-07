"""Scarica il dataset ufficiale AgentRisk in data/raw e registra la revisione.

Uso:  uv run python scripts/download_data.py [--revision SHA]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

REPO = "AgentRisk/agentrisk-data-2027"
DEST = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", default=None, help="SHA da fissare; default: ultima revisione")
    args = ap.parse_args()
    sha = args.revision or HfApi().dataset_info(REPO).sha
    path = snapshot_download(repo_id=REPO, repo_type="dataset", revision=sha, local_dir=DEST)
    (DEST / "REVISION.txt").write_text(f"{REPO}\n{sha}\n", encoding="utf-8")
    print(f"Scaricato {REPO} @ {sha} in {path}")


if __name__ == "__main__":
    main()
