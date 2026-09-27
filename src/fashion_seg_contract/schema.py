"""JSON Schema of one prediction (the model's response for one image), and typed views of it.

Example::

    {"height": 400, "width": 300, "instances": [
        {"class_id": 24, "label": "dress", "score": 0.97, "box": [12, 40, 380, 260],
         "mask_rle": "5230 12 5630 14"}]}

``box`` is ``[y1, x1, y2, x2]`` in pixels of the input image, ``(y2, x2)`` excluded; ``mask_rle``
is decoded with ``fashion_seg_contract.rle.decode(mask_rle, height, width)``.
"""

import json
from functools import cache
from importlib.resources import files
from typing import Any, TypedDict


class Instance(TypedDict):
    """One detected garment."""

    class_id: int
    label: str
    score: float
    box: list[int]
    mask_rle: str


class Prediction(TypedDict):
    """The model's response for one image."""

    height: int
    width: int
    instances: list[Instance]


@cache
def schema() -> dict[str, Any]:
    """The JSON Schema (draft 2020-12) shipped with this package."""
    text = files("fashion_seg_contract").joinpath("prediction.schema.json").read_text("utf-8")
    return json.loads(text)


def validate(prediction: dict[str, Any]) -> None:
    """Raise ``jsonschema.ValidationError`` if ``prediction`` breaks the contract.

    Needs the ``validate`` extra: ``fashion-seg-contract[validate]``.
    """
    import jsonschema  # pylint: disable=import-outside-toplevel  # optional dependency

    jsonschema.validate(prediction, schema())
