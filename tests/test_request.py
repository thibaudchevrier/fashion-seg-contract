"""Tests of the request format."""

import base64
import json

from fashion_seg_contract import request


def test_build_has_one_row_per_image_and_the_threshold():
    """Each image becomes one base64 row; min_score goes in the params, 0.7 by default."""
    body = request.build([b"a", b"bc"])
    assert [base64.b64decode(r["image"]) for r in body["dataframe_records"]] == [b"a", b"bc"]
    assert body["params"] == {"min_score": request.DEFAULT_MIN_SCORE}
    assert json.loads(json.dumps(body)) == body  # JSON-serializable as is
