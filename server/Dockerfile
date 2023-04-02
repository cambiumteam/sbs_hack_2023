FROM python:3.10-slim as python

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.3.1

# System dependencies.
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer.
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization.
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

# Copy python src.
COPY process.py /app/
COPY server /app/server

CMD [ "python", "process.py"]