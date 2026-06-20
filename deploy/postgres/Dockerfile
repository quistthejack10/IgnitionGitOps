# Custom Postgres image: Postgres 16 + Apache AGE (graph extension).
# TimescaleDB is added in M2 when time-series binding is wired; for the M1 benchmark
# spike only the graph engine is needed.
#
# Build context: repo root (docker-compose.yml uses `context: .`)
# Build time: 5-10 min on first pull (compiles AGE from source; cached on rebuild).

FROM postgres:16-bookworm AS builder

ENV AGE_TAG=PG16/v1.5.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libreadline-dev \
        zlib1g-dev \
        flex \
        bison \
        postgresql-server-dev-16 \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --branch "$AGE_TAG" --depth 1 \
        https://github.com/apache/age.git /tmp/age \
    && cd /tmp/age \
    && make \
    && make install \
    && rm -rf /tmp/age

# Final image: clean postgres:16 + only the compiled AGE extension files.
FROM postgres:16-bookworm

COPY --from=builder \
    /usr/lib/postgresql/16/lib/age.so \
    /usr/lib/postgresql/16/lib/

COPY --from=builder \
    /usr/share/postgresql/16/extension/age.control \
    /usr/share/postgresql/16/extension/age--1.5.0.sql \
    /usr/share/postgresql/16/extension/
