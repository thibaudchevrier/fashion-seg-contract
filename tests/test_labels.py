import json

from fashion_seg_contract.labels import BACKGROUND, load_class_names


def test_category_k_is_model_class_k_plus_one(tmp_path):
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({"categories": [{"id": 1, "name": "b"}, {"id": 0, "name": "a"}]}))
    assert load_class_names(labels) == [BACKGROUND, "a", "b"]
