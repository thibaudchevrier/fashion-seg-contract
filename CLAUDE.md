# CLAUDE.md

Guidance for working in this repository. Read it before changing anything.

## What this repo is

`fashion-seg-contract`: the **contract** (request and response) of the fashion segmentation
model, shared by the producer ([fashion-seg-train](https://github.com/thibaudchevrier/fashion-seg-train))
and its consumers ([fashion-serving](https://github.com/thibaudchevrier/fashion-serving)).

| Module | Content |
|--------|---------|
| `src/fashion_seg_contract/request.py` | `build()`: the request body; `IMAGE_FIELD`, `MIN_SCORE_PARAM`, `DEFAULT_MIN_SCORE` |
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

These standards are the same in the four repositories of the project (fashion-seg-contract,
maskrcnn-matterport-tf2, fashion-seg-train, fashion-serving). Keep them in sync.

### Environment

- **uv only** (never `pip install`): `uv add` / `uv add --dev` change dependencies and update
  `pyproject.toml` and `uv.lock` together; commit both.
- Packages from the other repositories are referenced by their **release wheel URL** in
  `[tool.uv.sources]`, like registry packages. Upgrade by changing the URL, then `uv lock`.
- Don't edit by hand: `uv.lock`, `CHANGELOG.md`, the `version` in `pyproject.toml` (commitizen owns
  the last two).
- Never commit secrets (`.dvc/*.local`, tokens) or large files (`check-added-large-files`
  blocks files over 1 MB: data and models go to DVC).

### Code quality: `make lint` = pre-commit hooks = CI

`.pre-commit-config.yaml` is the single definition of the checks. The git hooks (`make hooks`),
`make lint` and the CI lint job all run it, so a commit that passes locally passes in CI.

- **ruff format** (line length 100) and **ruff check**: pycodestyle, pyflakes, isort, pyupgrade,
  bugbear, comprehensions, simplify, and pydocstyle (numpy convention).
- **pydoclint**: every parameter, return value, yielded value, raised exception and class attribute
  is documented, with types matching the annotations.
- **pylint**: 10/10.
- Hygiene hooks: trailing whitespace, end of files, YAML/TOML syntax, merge conflicts, large files.
- A `# noqa: <code>` or `# pylint: disable=<name>` needs a reason on the same line. Never disable a
  check globally or raise a limit to make code pass: fix the code.

### Docstrings: numpy style, everywhere

Every module, class and function, public or private, has a
[numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) docstring:

```python
def decode(rle: str, height: int, width: int = 1) -> np.ndarray:
    """Decode an RLE string into a boolean mask.

    Parameters
    ----------
    rle : str
        Space-separated ``start length`` pairs, 1-indexed, column-major.
    height : int
        Mask height in pixels.
    width : int
        Mask width in pixels. By default 1.

    Returns
    -------
    np.ndarray
        Boolean mask of shape ``(height, width)``.

    Raises
    ------
    ValueError
        If the RLE has an odd number of values.

    Examples
    --------
    >>> decode("1 2", height=2).tolist()
    [[True], [True]]
    """
```

- Summary line in the imperative mood, ending with a period, then a blank line before sections.
- Types are written exactly like the annotations (`str | Path`, `dict[str, Any]`): pydoclint
  compares them. No `, optional` suffix: state the default in the description ("By default 1.").
- `Raises` lists the exceptions the function raises itself; mention exceptions propagated from
  callees in the description.
- Classes document their constructor parameters (`Parameters`) and attributes (`Attributes`) in the
  class docstring, not in `__init__`. Instance attributes are declared in the class body
  (`timeout: float`) so they can be checked.
- `Examples` are doctests: pytest runs them (`--doctest-modules`), so they must stay correct.
- Tests: a module docstring, and a one-line docstring per test saying which behaviour it checks.

### Code style

- Type-annotate every function signature, including private helpers.
- Import submodules explicitly (`from skimage import io, transform`), not several `import
  skimage.x` lines: linters can't tell which of those is unused. No re-export blocks: import from
  the module that defines the name.
- `pathlib.Path` over `os.path`, f-strings, no mutable default arguments, `logging` rather than
  `print` in library code, error messages that say what to do.
- Keep functions small enough for pylint's limits; split them rather than raising the limits.
- No duplicated code across repositories: shared code goes in a released package
  (fashion-seg-contract for the model's request and response, maskrcnn-matterport for Matterport
  code).

### Tests

- pytest, fast and offline by default. Every behaviour change or bug fix comes with a test.
- Tests that need data, models or services skip cleanly when they are missing (and run in CI when
  the credentials are set).
- `make check` (lint + tests) before every commit.

### Commits, PRs and releases

- [Conventional Commits](https://www.conventionalcommits.org/), checked by the `commit-msg` hook and
  on every PR: `type(scope): summary`, imperative, lower case, no final period. The body explains
  *why*. One logical change per commit.
- Types and their effect on the version (commitizen, `major_version_zero = true`):

  | Type | Release |
  |------|---------|
  | `feat` | minor |
  | `fix`, `perf`, `refactor` | patch |
  | `!` after the type, or a `BREAKING CHANGE:` footer | minor while < 1.0 (then major) |
  | `docs`, `style`, `test`, `ci`, `build`, `chore` | none |

- Work on a branch, open a PR, merge only when CI is green, with a **merge commit** (not squash: the
  individual conventional commits build the changelog). Never push to `main` directly: only the
  release workflow does (bump commit + tag).
- On merge, `release.yml` bumps the version, updates `CHANGELOG.md`, tags `vX.Y.Z` and publishes a
  GitHub Release (with the wheel and sdist for libraries).
