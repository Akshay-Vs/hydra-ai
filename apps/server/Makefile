.PHONY: build-wheel install-deps build-docker

build-wheel:
	uv venv
	uv pip install hatchling build
	uv run python -m build --wheel

install-deps:
	uv sync --frozen --no-cache --no-dev

build-docker:
	docker build -t server:latest .

clean:
	rm -rf dist/ build/ *.egg-info/ .venv/
