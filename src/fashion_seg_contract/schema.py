"""JSON Schema of one prediction (the model's response for one image), and typed views of it.

Examples
--------
A prediction::

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
    """One detected garment.

    Attributes
    ----------
    class_id : int
        Model class id, from 1 (0 is the background and never returned).
    label : str
        Class name.
    score : float
        Detection confidence, between 0 and 1.
    box : list[int]
        ``[y1, x1, y2, x2]`` in pixels of the input image, ``(y2, x2)`` excluded.
    mask_rle : str
        Instance mask, run-length encoded (see ``fashion_seg_contract.rle``).
    """

    class_id: int
    label: str
    score: float
    box: list[int]
    mask_rle: str


class Prediction(TypedDict):
    """The model's response for one image.

    Attributes
    ----------
    height : int
        Input image height in pixels.
    width : int
        Input image width in pixels.
    instances : list[Instance]
        Detected garments, possibly empty.
    """

    height: int
    width: int
    instances: list[Instance]


@cache
def schema() -> dict[str, Any]:
    """Load the JSON Schema shipped with this package.

    Returns
    -------
    dict[str, Any]
        The JSON Schema (draft 2020-12) of one prediction.
    """
    text = files("fashion_seg_contract").joinpath("prediction.schema.json").read_text("utf-8")
    return json.loads(text)


def validate(prediction: dict[str, Any]) -> None:
    """Check that a prediction follows the contract.

    Needs the ``validate`` extra (``fashion-seg-contract[validate]``). A prediction that breaks
    the contract makes ``jsonschema`` raise ``jsonschema.ValidationError``.

    Parameters
    ----------
    prediction : dict[str, Any]
        One prediction, as returned by the model for one image.
    """
    import jsonschema  # pylint: disable=import-outside-toplevel  # optional dependency

    jsonschema.validate(prediction, schema())
