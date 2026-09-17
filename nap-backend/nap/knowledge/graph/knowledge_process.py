"""
```
START --> convert --> vector --+-->  active --> END
                 |             |
                 +--> enrich --+
```
"""

from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import StateGraph, START, END
from nap.common.exceptions import KnowledgeProcessFailed
from nap.db.models import Knowledge, KnowledgeStatus
from nap.services.convert import CONVERT_SERVICE
from nap.services.vector import VECTOR_SERVICE
from nap.services.enrich import ENRICH_SERVICE


class State(TypedDict):
    knowledge: Knowledge
    content: str

    convert: NotRequired[bool]
    vector: NotRequired[bool]
    enrich: NotRequired[bool]


def _node_convert(state: State):
    todo = state["knowledge"].get_or_create_todo("convert")
    if todo.is_completed() and state["knowledge"].convert_path:
        return {
            "convert": True,
            "content": Path(state["knowledge"].convert_path).read_text(),
        }

    todo.set_running()
    content = CONVERT_SERVICE.convert(state["knowledge"])
    todo.set_completed()
    return {"convert": True, "content": content}


def _node_vector(state: State):
    todo = state["knowledge"].get_or_create_todo("vector")
    if todo.is_completed():
        return {"vector": True}

    todo.set_running()
    VECTOR_SERVICE.add_konwledge(state["knowledge"], state["content"])
    todo.set_completed()
    return {"vector": True}


def _node_enrich(state: State):
    todo = state["knowledge"].get_or_create_todo("enrich")
    if todo.is_completed():
        return {"enrich": True}
    todo.set_running()
    ENRICH_SERVICE.enrich(state["knowledge"], replace=True, content=state["content"])
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
