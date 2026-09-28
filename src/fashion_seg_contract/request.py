"""The request the model serves: one base64 image per row, and an optional ``min_score``.

Sent to ``POST /invocations`` of ``mlflow models serve`` (MLflow's ``dataframe_records`` format)::

    {"dataframe_records": [{"image": "<base64 jpeg/png>"}], "params": {"min_score": 0.8}}

The response has one prediction per row (see ``fashion_seg_contract.schema``).
"""

import base64
from typing import Any

IMAGE_FIELD = "image"
MIN_SCORE_PARAM = "min_score"
DEFAULT_MIN_SCORE = 0.7


def encode_image(data: bytes) -> str:
    """Encode an image file's bytes as the model expects them in a request.

    Parameters
    ----------
    data : bytes
        Encoded image (JPEG or PNG).

    Returns
    -------
    str
        Base64 (ASCII).

    Examples
    --------
    >>> encode_image(b"jpeg")
    'anBlZw=='
    """
    return base64.b64encode(data).decode("ascii")


def build(images: list[bytes], min_score: float = DEFAULT_MIN_SCORE) -> dict[str, Any]:
    """Build the body of a request for some images.

    Parameters
    ----------
    images : list[bytes]
        Encoded images (JPEG or PNG), one prediction each.
    min_score : float
        Detections below this confidence are dropped. By default ``DEFAULT_MIN_SCORE``.

    Returns
    -------
    dict[str, Any]
        JSON-serializable body for ``POST /invocations``.

    Examples
    --------
    >>> build([b"jpeg"], min_score=0.5)
    {'dataframe_records': [{'image': 'anBlZw=='}], 'params': {'min_score': 0.5}}
    """
    return {
        "dataframe_records": [{IMAGE_FIELD: encode_image(image)} for image in images],
        "params": {MIN_SCORE_PARAM: min_score},
    }
