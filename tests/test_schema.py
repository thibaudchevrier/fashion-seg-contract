import jsonschema
import pytest

from fashion_seg_contract import schema

VALID = {
    "height": 4,
    "width": 3,
    "instances": [
        {"class_id": 24, "label": "dress", "score": 0.9, "box": [0, 0, 2, 2], "mask_rle": "1 2"}
    ],
}


def test_valid_prediction_passes():
    schema.validate(VALID)
    schema.validate({"height": 1, "width": 1, "instances": []})


@pytest.mark.parametrize(
    "broken",
    [
        {"height": 4, "width": 3, "detections": []},  # renamed field
        {**VALID, "instances": [{**VALID["instances"][0], "class_id": 0}]},  # background
        {**VALID, "instances": [{**VALID["instances"][0], "box": [0, 0, 2]}]},  # 3 coords
        {**VALID, "instances": [{**VALID["instances"][0], "mask_rle": "1 2 3"}]},  # odd RLE
    ],
)
def test_breaking_changes_are_rejected(broken):
    with pytest.raises(jsonschema.ValidationError):
        schema.validate(broken)


def test_optional_fields_are_backward_compatible():
    schema.validate({**VALID, "model_version": "5"})
