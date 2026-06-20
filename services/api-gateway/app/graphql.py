"""GraphQL surface (FR-M5).

In M2 the schema is *generated* from the user's data model (model.schema.json) by graph-core,
Rhize-style: every entity and relationship type becomes immediately queryable and mutable with
filtering, pagination, and nested traversal. This M0 stub serves a minimal placeholder schema
so the /graphql endpoint is live.
"""

from __future__ import annotations

import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    def status(self) -> str:
        """Placeholder. Replaced by the model-generated schema in M2."""
        return "forge graphql online; schema generated from data model in M2"


schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema)
