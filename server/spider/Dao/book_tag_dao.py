from .base_dao import BaseDAO
import mysql.connector


class BookTagDAO(BaseDAO):
    def __init__(self, db_config):
        super().__init__(db_config)

    def add_book_tag_relations(self, relations_to_insert):
        """
        向 book_tag 表中批量插入书籍与标签的关联关系。
        """
        if not relations_to_insert:
            return 0

        with self as dao:
            try:
                query = "INSERT IGNORE INTO book_tag (book_id, book_tag) VALUES (%s, %s)"
                dao.cursor.executemany(query, relations_to_insert)

                # 手动提交事务
                dao.connection.commit()

                return dao.cursor.rowcount
            except mysql.connector.Error as err:
                print(f"BookTagDAO 插入失败: {err}")
                # 手动回滚事务
                dao.connection.rollback()
                raise