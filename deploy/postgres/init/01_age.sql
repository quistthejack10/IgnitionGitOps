-- Runs automatically on first database initialisation (docker-entrypoint-initdb.d).
-- Enables the Apache AGE graph extension and creates the 'forge' property graph.
-- LOAD 'age' and search_path are session-level; AgeStore.connect() handles those per
-- connection. This file is idempotent (IF NOT EXISTS).

CREATE EXTENSION IF NOT EXISTS age;

LOAD 'age';
SET search_path = ag_catalog, "$user", public;

SELECT create_graph('forge');
