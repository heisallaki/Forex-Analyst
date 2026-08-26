import json
from datetime import UTC, datetime
from pathlib import Path

import joblib

from app.core.config import settings


def _model_dir(model_name: str) -> Path:
    directory = Path(settings.MODEL_STORAGE_PATH) / model_name
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_model(model_name: str, model, metadata: dict) -> str:
    directory = _model_dir(model_name)
    version = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")

    model_path = directory / f"{version}.joblib"
    joblib.dump(model, model_path)

    metadata_with_version = dict(metadata)
    metadata_with_version["version"] = version
    metadata_with_version["trained_at"] = datetime.now(UTC).isoformat()
    metadata_path = directory / f"{version}.json"
    metadata_path.write_text(json.dumps(metadata_with_version, indent=2))

    latest_pointer_path = directory / "latest.json"
    latest_pointer_path.write_text(json.dumps({"version": version}))

    return version


def load_latest_model(model_name: str):
    directory = _model_dir(model_name)
    latest_pointer_path = directory / "latest.json"
    if not latest_pointer_path.exists():
        return None, None

    version = json.loads(latest_pointer_path.read_text())["version"]
    model_path = directory / f"{version}.joblib"
    metadata_path = directory / f"{version}.json"
    if not model_path.exists():
        return None, None

    model = joblib.load(model_path)
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    return model, metadata
