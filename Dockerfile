# NOTE: BUILDTIME environment variables are utilized here
FROM python:3.11-slim as base
ARG INSTALL_DEV_DEPS=false
WORKDIR /app
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY --chmod=755 scripts/ ./scripts/
RUN pip install uv 
RUN INSTALL_DEV_DEPS=${INSTALL_DEV_DEPS} ./scripts/setup_venv.sh

FROM python:3.11-slim as runner
ENV PYTHONPATH=/app/src

# NON-ROOT USER DOES NOT EXIST IN THE BASE IMAGE, SO WE NEED TO CREATE IT
RUN groupadd -r -g 1000 python && useradd -r -u 1000 -g python python
WORKDIR /app
COPY --chown=python:python --chmod=755 scripts/ ./scripts/
COPY --chown=python:python --from=base /app/.venv/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=python:python src/ ./src/

# ENSURE NON-ROOT USER IS USED FOR THE CONTAINER FOR SECURITY
USER python
EXPOSE 8000 5678

CMD ["./scripts/start.sh"] 