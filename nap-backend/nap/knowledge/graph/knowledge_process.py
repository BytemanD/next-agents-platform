"""
```
START --> convert --> vector --+-->  active --> END
                 |             |
                 +--> enrich --+
```
"""

import os
from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import StateGraph, START, END
from pystonic.common import context

from nap.storage import get_storage_driver
from nap.common.conf import CONF
from nap.common.exceptions import KnowledgeProcessFailed
from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.enrich_drivers.agent import EnrichmentAgentDriver
from nap.knowledge.vector_drivers.chromadb import ChromadbDriver
from nap.knowledge.parse_drivers.markitdown import MarkitdownDriver


class State(TypedDict):
    knowledge: Knowledge
    content: str

    convert: NotRequired[bool]
    vector: NotRequired[bool]
    enrich: NotRequired[bool]


parse_driver = MarkitdownDriver()
vector_driver = ChromadbDriver()
storage_driver = get_storage_driver()


def _node_convert(state: State):
    todo = state["knowledge"].get_or_create_todo("convert")
    if todo.is_completed() and state["knowledge"].convert_path:
        return {
            "convert": True,
            "content": Path(state["knowledge"].convert_path).read_text(),
        }

    convert_path = Path(
        CONF.store,
        "convert",
        state["knowledge"].uuid,
        os.path.basename(state["knowledge"].raw_path),
    )
    convert_path.parent.mkdir(parents=True, exist_ok=True)

    todo.set_running()
    file_path = storage_driver.get_path(state["knowledge"].raw_path)
    content = parse_driver.convert(str(file_path))
    storage_driver.save(str(convert_path), content)

    state["knowledge"].convert_path = str(convert_path)
    state["knowledge"].save()
    todo.set_completed()
    return {"convert": True, 'content': content}


def _node_vector(state: State):
    todo = state["knowledge"].get_or_create_todo("vector")
    if todo.is_completed():
        return {"vector": True}

    todo.set_running()
    vector_driver.add_konwledge(state["knowledge"], state["content"])
    todo.set_completed()
    return {"vector": True}


def _node_enrich(state: State):
    todo = state["knowledge"].get_or_create_todo("enrich")
    if todo.is_completed():
        return {"enrich": True}
    todo.set_running()
    driver = EnrichmentAgentDriver()
    driver.enrich(state["knowledge"], replace=True, content=state["content"])
    todo.set_completed()
    return {"enrich": True}


def _node_active(state: State):
    if all([state.get("convert"), state.get("vector"), state.get("enrich")]):
        state["knowledge"].set_status(KnowledgeStatus.active)
    else:
        state["knowledge"].set_status(KnowledgeStatus.pending_process)
    return state


# graph = StateGraph(State)
# graph.add_node("convert", _node_convert)
# graph.add_node("vector", _node_vector)
# graph.add_node("enrich", _node_enrich)
# graph.add_node("active", _node_active)

# graph.add_edge(START, "convert")
# graph.add_edge("convert", "vector")
# graph.add_edge("convert", "enrich")

# graph.add_edge(["vector", "enrich"], "active").add_edge
# graph.add_edge("active", END)


# graph.invoke(knowledge)
INGEST_GRAPH = (
    StateGraph(State)
    .add_node("convert", _node_convert)
    .add_node("vector", _node_vector)
    .add_node("enrich", _node_enrich)
    .add_node("active", _node_active)
    .add_edge(START, "convert")
    .add_edge("convert", "vector")
    .add_edge("convert", "enrich")
    .add_edge(["vector", "enrich"], "active")
    .add_edge("active", END)
    .compile()
)


def run(knowledge: Knowledge):
    if not knowledge.raw_path:
        raise KnowledgeProcessFailed(knowledge.uuid, "knowledge raw path is empty")

    INGEST_GRAPH.invoke(State(knowledge=knowledge, content=""))
