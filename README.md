# fashion-seg-contract

The **contract** of the fashion segmentation model: the request it accepts, what it returns for an
image, and the helpers to build and read them. It is the only code shared by the producer and the
consumers:

```
fashion-seg-train  ──(packages the model, it serves this contract)──►  fashion-seg-contract
fashion-serving    ──(builds requests and reads responses with)─────►  fashion-seg-contract
```

Depends on numpy only (1.x or 2.x), so it installs next to TensorFlow 2.15, TensorFlow 2.21 or
PyTorch alike.

| Module | Content |
|--------|---------|
| `fashion_seg_contract.request` | `build(images, min_score)`: the request body; `IMAGE_FIELD`, `DEFAULT_MIN_SCORE` |
| `fashion_seg_contract.schema` | The JSON Schema of one prediction (`schema()`), `validate()`, and `Prediction` / `Instance` typed dicts |
| `fashion_seg_contract.rle` | `encode(mask)` / `decode(rle, height, width)` for `mask_rle` (the iMaterialist annotation encoding) |
| `fashion_seg_contract.labels` | `load_class_names(label_descriptions.json)`: model class id → name (0 = background) |

## The contract

Request, one row per image (MLflow's `dataframe_records`; `min_score` defaults to 0.7):

```json
{"dataframe_records": [{"image": "<base64 jpeg/png>"}], "params": {"min_score": 0.8}}
```

Response, one prediction per image:

```json
{"height": 400, "width": 300, "instances": [
  {"class_id": 24, "label": "dress", "score": 0.97, "box": [12, 40, 380, 260], "mask_rle": "5230 12 5630 14"}
]}
```

- `box`: `[y1, x1, y2, x2]` in pixels of the input image, `(y2, x2)` excluded.
- `mask_rle`: space-separated `start length` pairs, 1-indexed, pixels in column-major order.
- `class_id`: model class id, from 1 to 46 (dataset category `k` is model class `k + 1`).

**Compatibility rule:** adding optional fields is backward compatible (minor release); renaming,
removing or retyping a field is a breaking change (`feat!:` commit), and consumers must be updated
before the producer ships it.

## Install

```toml
# pyproject.toml of a consumer
dependencies = ["fashion-seg-contract"]            # or "fashion-seg-contract[validate]"

[tool.uv.sources]
fashion-seg-contract = { git = "https://github.com/thibaudchevrier/fashion-seg-contract", tag = "v0.1.0" }
```

Each release also attaches its wheel to the
[GitHub Release](https://github.com/thibaudchevrier/fashion-seg-contract/releases); a wheel URL works
as a source too (e.g. in an MLflow model's `requirements.txt`). GitHub Packages has no Python
registry, so releases carry the built packages.

```python
from fashion_seg_contract import rle, schema

schema.validate(prediction)                       # needs the `validate` extra
mask = rle.decode(inst["mask_rle"], prediction["height"], prediction["width"])
```

## Development

```bash
make install   # all extras + dev tools
make hooks     # once: pre-commit and commit-msg git hooks
make check     # lint (all pre-commit hooks, exactly what CI runs) + tests (incl. doctests)
```

Code quality is defined once, in `.pre-commit-config.yaml`: ruff (format, lint, numpy docstrings),
pydoclint (every parameter, return and exception documented) and pylint (10/10). The git hooks,
`make lint` and CI all run it. Conventions for contributors (and for Claude Code) are in
[`CLAUDE.md`](CLAUDE.md).

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), checked by the
`commit-msg` hook and on every PR. On every merge to `main`, commitizen bumps the version for
`feat` (minor) and `fix`/`perf`/`refactor` (patch) commits (breaking changes bump the minor version while
< 1.0), updates `CHANGELOG.md`, tags `vX.Y.Z` and publishes a GitHub Release with the wheel and sdist.

CI runs the tests on Python 3.11 with the oldest supported dependencies (numpy 1.x) and on
Python 3.12 with the newest (numpy 2.x): the two environments this package is used in.
