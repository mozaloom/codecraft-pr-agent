install:
   uv sync --all-extras

test:
	uv run pytest test_server.py -v

format:
	black *.py tools/*.py

lint:
	pylint --disable=R,C,E1120 *.py

run:
	uv run server.py