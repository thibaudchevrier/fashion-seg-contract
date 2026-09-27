# CLAUDE.md

Guidance for working in this repository. Read it before changing anything.

## What this repo is

`fashion-seg-contract`: the **response contract** of the fashion segmentation model, shared by the
producer ([fashion-seg-train](https://github.com/thibaudchevrier/fashion-seg-train)) and its
consumers ([fashion-serving](https://github.com/thibaudchevrier/fashion-serving)).

| Module | Content |
|--------|---------|
| `src/fashion_seg_contract/schema.py` | JSON Schema of one prediction (`prediction.schema.json`, package data), `validate()`, `Prediction` / `Instance` typed dicts |
| `src/fashion_seg_contract/rle.py` | `encode` / `decode` of `mask_rle` |
| `src/fashion_seg_contract/labels.py` | `load_class_names()`: model class id → name |

Consumers install it by **release wheel URL** (`[tool.uv.sources]`), like a registry package.

### Rules specific to this repo

- **Dependencies stay minimal**: numpy only (plus `jsonschema` in the `validate` extra). This
  package is installed next to TensorFlow 2.15 (numpy 1.x, Python 3.11) and TensorFlow 2.21 /
  PyTorch (numpy 2.x, Python 3.12): anything added must work in both. CI tests both ends
  (oldest dependencies on 3.11, newest on 3.12).
- **Compatibility**: adding an optional field is backward compatible (`feat:`). Renaming,
  removing or retyping a field, or changing the RLE format, is breaking (`feat!:` + `BREAKING
  CHANGE:` footer). Consumers must adopt a breaking release before the producer ships it.
- Never duplicate this code elsewhere: other repos depend on the package.

## Commands

```bash
make install   # uv sync --locked --all-extras
make hooks     # once: install the pre-commit and commit-msg git hooks
make format    # ruff format + ruff --fix
make lint      # all pre-commit hooks on all files (exactly what CI runs)
make test      # pytest, including docstring examples (doctests)
make check     # lint + test: run before every commit
```

## Standards

### Environment

- **uv only** (never `pip install`): `uv add` / `uv add --dev` to change dependencies, which
  updates `pyproject.toml` and `uv.lock` together. Commit both.
- Don't edit by hand: `uv.lock`, `CHANGELOG.md`, the `version` in `pyproject.toml` (commitizen
  owns the last two).

### Code quality (enforced: `make lint` = pre-commit = CI)

`.pre-commit-config.yaml` is the single definition of the checks; CI runs the same hooks.

- **ruff format** (line length 100) and **ruff check**: pycodestyle, pyflakes, isort, pyupgrade,
  bugbear, comprehensions, simplify, and pydocstyle with the numpy convention.
- **pydoclint**: every parameter, return value, yielded value, raised exception and class
  attribute is documented, with types matching the annotations.
- **pylint**: must stay at 10/10.
- A `# noqa: <code>` or `# pylint: disable=<name>` needs a reason on the same line. Never
  disable a check globally to make code pass.

### Docstrings: numpy style, everywhere

Every module, class and function (public or private) has a
[numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) docstring:

```python
def decode(rle: str, height: int, width: int) -> np.ndarray:
    """Decode an RLE string into a boolean mask.

    Parameters
    ----------
    rle : str
        Space-separated ``start length`` pairs, 1-indexed, column-major.
    height : int
        Mask height in pixels.

    Returns
    -------
    np.ndarray
        Boolean mask of shape ``(height, width)``.

    Raises
    ------
    ValueError
        If ...

    Examples
    --------
    >>> decode("1 2", height=2, width=1).tolist()
    [[True], [True]]
    """
```

- Summary line in the imperative mood, ending with a period; blank line before sections.
- Types in `Parameters` / `Returns` are written exactly like the annotations (`str | Path`,
  `dict[str, Any]`): pydoclint compares them.
- Classes document their constructor parameters and their `Attributes` in the class docstring.
- `Examples` are doctests: pytest runs them, so they must stay correct.
- Tests: a module docstring and a one-line docstring per test saying what behaviour it checks.

### Code style

- Type-annotate every function signature (including private helpers).
- Import submodules explicitly (`from skimage import io`, not `import skimage.io` next to other
  `skimage.*` imports) so linters can detect unused imports. No re-export blocks.
- `pathlib.Path` over `os.path`; f-strings; no mutable default arguments; no `print` in library
  code.
- Keep functions small enough for pylint's limits instead of raising the limits.

### Tests

- pytest; tests are fast and offline. Every behaviour change or bug fix comes with a test.
- The contract has negative tests: a change that should be breaking must make one fail.

### Commits, PRs and releases

- [Conventional Commits](https://www.conventionalcommits.org/), checked by the `commit-msg` hook
  and on every PR: `type(scope): summary`, imperative, lower case, no period.
- Types and their effect on the version (commitizen, `major_version_zero = true`):

  | Type | Release |
  |------|---------|
  | `feat` | minor |
  | `fix`, `perf`, `refactor` | patch |
  | `!` / `BREAKING CHANGE:` footer | minor while < 1.0 (then major) |
  | `docs`, `style`, `test`, `ci`, `build`, `chore` | none |

- One logical change per commit; the body explains *why*.
- Work on a branch, open a PR, merge only when CI is green, with a **merge commit** (not squash:
  the individual conventional commits drive the changelog). Never push to `main` directly: only
  the release workflow does (bump commit + tag).
- On merge, `release.yml` bumps the version, updates `CHANGELOG.md`, tags `vX.Y.Z` and publishes a
  GitHub Release with the wheel and sdist.
