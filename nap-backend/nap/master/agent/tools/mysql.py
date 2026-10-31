from typing import Any

import pymysql
from langchain_core.tools import tool
from loguru import logger

from nap.common.objects import Toolkit, ToolkitMetadata


class MysqlToolkit(Toolkit):
    database: str
    host: str
    port: int
    user: str
    password: str
    charset: str = "utf8mb4"
    autocommit: bool = True
    # title: str = "MySQL查询"
    # type: str = "db"
    # help: str = ""
    # args_schema: dict = MysqlTookitConfig.model_json_schema()
    # config: dict = {}

    @classmethod
    def metadata(cls):
        return ToolkitMetadata(
            name="mysql",
            title="MySQL查询",
            type="db",
            help="MySQL数据库查询工具",
        )

    def connect_db(self):
        return pymysql.connect(
            database=self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            charset=self.charset,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def get_tools(self):
        @tool(
            parse_docstring=True,
        )
        def execute_sql(sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any]:
            """执行Mysql SQL 语句

            需要注意的是，如果SQL包含模糊匹配符号 `%`, 传入的sql 中的`%`应该替换为 `%%`,
            避免格式化错误。

            Args:
                sql: SQL 语句，使用 ? 或 :name 占位符防止注入
                parameters: 可选参数，与占位符匹配

            Returns:
                {
                    "rows": [...],
                    "affected_rows": 影响行数,
                    "last_row_id": 最后插入行的ID(若适用)
                }

            Example:
                execute_sql("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
                execute_sql("INSERT INTO users (name) VALUES (?)", ("Alice",))
                result = execute_sql("SELECT * FROM users")  # 得到查询结果
            """

            conn = self.connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute(sql, parameters or ())
                last_id = cursor.lastrowid
                if not conn.autocommit_mode:
                    conn.commit()

                return {
                    "rows": [dict(x) for x in cursor.fetchall()],
                    "affected_rows": cursor.rowcount,
                    "last_row_id": last_id if last_id != 0 else None,
                }
            except Exception as e:
                logger.exception("execute SQL {} failed: {}", sql, e)
                conn.rollback()
                raise RuntimeError(f"SQL execution failed: {e}") from e

        return []
