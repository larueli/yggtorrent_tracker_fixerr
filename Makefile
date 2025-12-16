# Use bash for improved behavior
SHELL := /bin/bash

.PHONY: dev update setup

dev:
	uv run litestar run --host "0.0.0.0" --port "8000" --reload

update:
	uv sync --dev --upgrade
	uv run pre-commit autoupdate

setup:
	/usr/local/bin/uv sync --dev --frozen && \
	/usr/local/bin/uv run pre-commit install --hook-type commit-msg --hook-type pre-push --hook-type pre-commit
