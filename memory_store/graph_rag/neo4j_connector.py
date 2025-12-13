from __future__ import annotations
from dataclasses import dataclass
from neo4j import GraphDatabase
from typing import Iterable

@dataclass
class Neo4jConfig:
    uri: str
    user: str
    password: str

class Neo4jConnector:
    def __init__(self, cfg: Neo4jConfig):
        self._driver = GraphDatabase.driver(cfg.uri, auth=(cfg.user, cfg.password))

    def close(self):
        self._driver.close()

    def ensure_schema(self) -> None:
        q = "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE"
        with self._driver.session() as s:
            s.run(q)

    def upsert_triplets(self, triplets: Iterable[tuple[str, str, str, str]]) -> None:
        q = """
        MERGE (s:Entity {id: $sid})
          ON CREATE SET s.name = $sname
          ON MATCH SET s.name = coalesce(s.name, $sname)
        MERGE (o:Entity {id: $oid})
          ON CREATE SET o.name = $oname
          ON MATCH SET o.name = coalesce(o.name, $oname)
        MERGE (s)-[r:REL {type: $pred}]->(o)
        """
        with self._driver.session() as s:
            for sid, sname, pred, oname in triplets:
                oid = f"ent_{abs(hash(oname)) % (10**12)}"
                s.run(q, sid=sid, sname=sname, pred=pred, oid=oid, oname=oname)

    def neighborhood(self, entity_name: str, limit: int = 25) -> list[dict]:
        q = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($name)
        MATCH (e)-[r:REL]->(o:Entity)
        RETURN e.name as subject, r.type as predicate, o.name as object
        LIMIT $limit
        """
        with self._driver.session() as s:
            rows = s.run(q, name=entity_name, limit=limit)
            return [dict(r) for r in rows]
