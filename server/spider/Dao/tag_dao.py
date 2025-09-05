# 文件路径: server/dao/tag_dao.py

from .base_dao import BaseDAO
import mysql.connector


class TagDAO(BaseDAO):
    def __init__(self, db_config):
        super().__init__(db_config)

    def get_tags(self, limit=None):  # 此处也做了统一修改
        """
        从数据库中查询标签，可以选择性地限制数量。
        """
        # with self as dao: 会自动连接和关闭
        with self as dao:
            query = "SELECT tag FROM tags"
            params = []

            if limit and isinstance(limit, int) and limit > 0:
                query += " LIMIT %s"
                params.append(limit)

            dao.cursor.execute(query, params)
            tags = [item[0] for item in dao.cursor.fetchall()]
            return tags

    def add_new_tags(self, new_tags_to_insert):
        """
        向数据库中批量插入新标签。
        """
        if not new_tags_to_insert:
            return 0

        # with self as dao: 会自动连接和关闭
        with self as dao:
            try:
                query = "INSERT INTO tags (main_tag, tag) VALUES (%s, %s)"
                dao.cursor.executemany(query, new_tags_to_insert)

                # 【核心修改】手动提交事务
                dao.connection.commit()

                return dao.cursor.rowcount
            except mysql.connector.Error as err:
                print(f"TagDAO 插入失败: {err}")
                # 【核心修改】手动回滚事务
                dao.connection.rollback()
                raise