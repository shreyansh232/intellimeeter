.PHONY: install tests run lint clean

install:
	uv sync

tests:
	PYTHONPATH=. uv run pytest tests/

run:
	uv run uvicorn app.main:app --reload

lint:
	uv run ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
