"""Class labels: iMaterialist categories mapped to model class ids."""

import json
from pathlib import Path

BACKGROUND = "BG"


def load_class_names(label_file: str | Path) -> list[str]:
    """Read the model class names from ``label_descriptions.json``.

    The model reserves id 0 for the background, so dataset category ``k`` is model class
    ``k + 1``.

    Parameters
    ----------
    label_file : str | Path
        Path to the iMaterialist ``label_descriptions.json``.

    Returns
    -------
    list[str]
        Class names indexed by model class id, starting with ``BACKGROUND``.
    """
    categories = json.loads(Path(label_file).read_text(encoding="utf-8"))["categories"]
    ordered = sorted(categories, key=lambda c: c["id"])
    return [BACKGROUND] + [c["name"] for c in ordered]
