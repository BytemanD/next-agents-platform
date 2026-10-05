"""一次性数据迁移：Agents.tools 从 list[str] 改为 dict[str, dict]。

结构变化：
    旧: ["web_search", "retrival"]
    新: {"web_search": {}, "retrival": {}}

同时把已废弃字段 tool_args 里的参数合并进新结构，避免数据丢失。
可重复执行（幂等）：已是 dict 的记录会跳过。
"""

from nap.db.models import Agents


def migrate() -> int:
    changed = 0
    for agent in Agents.query():
        tools = agent.tools
        if not isinstance(tools, list):
            continue

        args = agent.tool_args if isinstance(agent.tool_args, dict) else {}
        new_tools: dict[str, dict] = {}
        for name in tools:
            params = args.get(name)
            new_tools[name] = params if isinstance(params, dict) else {}

        agent.tools = new_tools
        agent.tool_args = {}
        agent.save()
        changed += 1
        print(f"migrated {agent.uuid}: {tools} -> {list(new_tools)}")
    return changed


if __name__ == "__main__":
    n = migrate()
    print(f"done, {n} agent(s) migrated")