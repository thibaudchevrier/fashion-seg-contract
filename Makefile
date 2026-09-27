# Same commands locally and in CI (.github/workflows/ci.yml).
PYLINT_TESTS_DISABLE = missing-module-docstring,missing-function-docstring,redefined-outer-name

.PHONY: install format lint test check

install:
	uv sync --locked --all-extras

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

lint:
	uv run ruff format --check src tests
	uv run ruff check src tests
	uv run pylint src
	uv run pylint tests/*.py --disable=$(PYLINT_TESTS_DISABLE)

test:
	uv run pytest

check: lint test
