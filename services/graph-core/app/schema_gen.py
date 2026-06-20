"""Generate the GraphQL schema from a user-defined Model (FR-M5).

This is the Rhize-style move: the user's ontology *is* the API. M2 implements the real
strawberry schema generation (query types, filters, pagination, nested relationship
traversal) plus parallel REST CRUD. This M0 stub validates the contract and sketches the map.
"""

from __future__ import annotations

from app.model import Model, PropertyType

_GQL_SCALARS: dict[PropertyType, str] = {
    "string": "String",
    "number": "Float",
    "boolean": "Boolean",
    "datetime": "DateTime",
    "enum": "String",
    "json": "JSON",
    "fileref": "String",
}


def generate_graphql_sdl(model: Model) -> str:
    """Return a best-effort GraphQL SDL sketch for the model.

    M0: emits a readable type-per-entity sketch to prove the mapping. M2 replaces this with a
    real strawberry schema wired to the PropertyGraphStore (filtering, pagination, traversal).
    """
    lines: list[str] = [f"# Generated from model '{model.name}' v{model.version}"]
    for et in model.entityTypes:
        lines.append(f"type {et.name} {{")
        lines.append("  id: ID!")
        for prop in et.properties:
            scalar = _GQL_SCALARS.get(prop.type, "String")
            bang = "!" if prop.required else ""
            lines.append(f"  {prop.name}: {scalar}{bang}")
        # Relationships where this entity is the source become traversable fields.
        for rel in model.relationshipTypes:
            if rel.from_ == et.name:
                lines.append(f"  {rel.name.lower()}: [{rel.to}!]!  # via {rel.name}")
        lines.append("}")
    return "\n".join(lines)
