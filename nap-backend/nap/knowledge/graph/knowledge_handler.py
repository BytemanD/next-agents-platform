from typing import TypedDict

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END

from loguru import logger
from nap.db.models import Knowledge, KnowledgeStatus
from nap.knowledge.drivers.chromadb import ChromadbDriver
from nap.knowledge.parse_drivers.markitdown import MarkitdownDriver
from pydantic import BaseModel


class State(TypedDict):
    knowledge: Knowledge
    content: str | None
    root_count: int


parse_driver = MarkitdownDriver()
vector_driver = ChromadbDriver()


def _judge_knowledge_status(state: State):
    return KnowledgeStatus(state["knowledge"].status).name

def _node_root(state: State):
    state['root_count'] += 1
    return state


def _node_parse(state: State):
    try:
        state["content"] = parse_driver.parse(state["knowledge"])
        logger.success('parse success ...')
    except Exception:
        state["knowledge"].set_status(KnowledgeStatus.parse_failed)
    return state


def _node_vector(state: State):
    if not state["content"]:
        return state
    vector_driver.add_konwledge(state["knowledge"], state["content"])
    return state


def _node_delete_from_vector(state: State):
    vector_driver.delete_knowledge(state["knowledge"])
    return state


def _node_delete_from_db(state: State):
    state["knowledge"].delete()
    return state




"""
START -> parse -> vector -> END
           |
           +- failed ---> END
      -> delete_from_vector -> delete_from_db -> END
                        |
                        +----> END
"""

graph = StateGraph(State)
graph.add_node("root", _node_root)
graph.add_node("parse", _node_parse)
graph.add_node("vector", _node_vector)
graph.add_node("delete_from_vector", _node_delete_from_vector)
graph.add_node("delete_from_db", _node_delete_from_db)

graph.add_edge(START, 'root')
graph.add_conditional_edges(
    'root',
    _judge_knowledge_status,
    {
        KnowledgeStatus.parse_pending.name: "parse",
        KnowledgeStatus.parse_completed.name: "vector",
        KnowledgeStatus.delete_pending.name: "delete_from_vector",
        KnowledgeStatus.delete_completed.name: "delete_from_db",
        # 其他状态
        KnowledgeStatus.vector_completed.name: END,
        KnowledgeStatus.save_waiting.name: END,
        KnowledgeStatus.save_running.name: END,
        KnowledgeStatus.save_failed.name: END,
        KnowledgeStatus.save_completed.name: END,
        KnowledgeStatus.parse_running.name: END,
        KnowledgeStatus.parse_failed.name: END,
        KnowledgeStatus.delete.name: END,
        KnowledgeStatus.delete_failed.name: END,
        KnowledgeStatus.delete_running.name: END,
    },
)
graph.add_edge("parse", 'root')
graph.add_edge("vector", 'root')
graph.add_edge("delete_from_vector", 'root')
graph.add_edge("delete_from_db", END)

# graph.invoke(knowledge)
INGEST_GRAPH = graph.compile()


def run(knowledge: Knowledge):
    INGEST_GRAPH.invoke(State(knowledge=knowledge, content=None, root_count=0))
