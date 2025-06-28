default:
    just --list

_format:
    ruff format src tests

_isort:
    ruff check --select I --fix src tests

fmt: && _isort _format

lint:
    ruff check --fix src tests
    basedpyright src tests

test:
    pytest
