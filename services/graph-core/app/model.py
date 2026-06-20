"""Typed mirror of schemas/model.schema.json.

graph-core reads a `Model` to (a) provision storage and (b) generate the GraphQL/REST API.
Mirroring the JSON Schema as pydantic models gives validated, ergonomic access in Python.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PropertyType = Literal["string", "number", "boolean", "datetime", "enum", "json", "fileref"]
Cardinality = Literal["one-to-one", "one-to-many", "many-to-one", "many-to-many"]


class Property(BaseModel):
    name: str
    type: PropertyType
    required: bool = False
    enumValues: list[str] | None = None
    computed: bool = False


class TelemetryChannel(BaseModel):
    name: str
    unit: str | None = None
    retention: str | None = None


class EntityType(BaseModel):
    name: str
    properties: list[Property] = Field(default_factory=list)
    telemetryChannels: list[TelemetryChannel] = Field(default_factory=list)


class RelationshipType(BaseModel):
    name: str
    from_: str = Field(alias="from")
    to: str
    cardinality: Cardinality = "many-to-many"
    properties: list[Property] = Field(default_factory=list)


class Model(BaseModel):
    name: str
    version: int
    description: str | None = None
    entityTypes: list[EntityType] = Field(default_factory=list)
    relationshipTypes: list[RelationshipType] = Field(default_factory=list)
