from .author_dao import AuthorDAO
from .base_dao import BaseDAO
import mysql.connector


class BookDAO(BaseDAO):
    def __init__(self, db_config):
        super().__init__(db_config)
        self.author_dao = AuthorDAO(db_config)

    def ensure_books_exist(self, book_ids):
        """
        确保一批 book_id 存在于 cleaned_douban_books 表中。
        """
        if not book_ids:
            return 0

        unique_book_ids = set(book_ids)

        # with self as dao: 会自动连接和关闭
        with self as dao:
            try:
                # 1. 查询
                format_strings = ','.join(['%s'] * len(unique_book_ids))
                query_existing = f"SELECT book_id FROM cleaned_douban_books WHERE book_id IN ({format_strings})"
                dao.cursor.execute(query_existing, tuple(unique_book_ids))
                existing_ids = {row[0] for row in dao.cursor.fetchall()}

                # 2. 计算
                new_ids_to_insert = list(unique_book_ids - existing_ids)

                if not new_ids_to_insert:
                    return 0

                # 3. 插入
                query_insert = "INSERT INTO cleaned_douban_books (book_id) VALUES (%s)"
                data_to_insert = [(book_id,) for book_id in new_ids_to_insert]
                dao.cursor.executemany(query_insert, data_to_insert)

                # 【核心修改】手动提交事务
                dao.connection.commit()

                return dao.cursor.rowcount
            except mysql.connector.Error as err:
                print(f"BookDAO 插入失败: {err}")
                # 【核心修改】手动回滚事务
                dao.connection.rollback()
                raise

    def update_book_details(self, book_id, book_data):
        if not book_data:
            return 0

        # 【关键】建立Python字典键到数据库列名的映射
        column_mapping = {
            'title': 'title',
            'img_src': 'img_src',
            # 'author_name': 'author_id', # 作者需要特殊处理
            'publisher': 'publisher',
            'producer': 'producer',
            'original_title': 'original_title',
            'translator': 'translator',
            'publication_year': 'publication_year',
            'page_count': 'page_count',
            'price': 'price',
            'binding': 'binding',
            'series': 'series',
            'isbn': 'isbn',
            'rating': 'rating',
            'rating_sum': 'rating_sum',
            'stars5_starstop': 'stars5_starstop',
            'stars4_starstop': 'stars4_starstop',
            'stars3_starstop': 'stars3_starstop',
            'stars2_starstop': 'stars2_starstop',
            'stars1_starstop': 'stars1_starstop'
        }

        set_clauses = []
        params = []
        for py_key, db_col in column_mapping.items():
            if py_key in book_data and book_data[py_key] is not None:
                set_clauses.append(f"{db_col} = %s")
                params.append(book_data[py_key])


        author_name_full = book_data.get('author_name')
        if author_name_full:
            try:
                author_id = self.author_dao.get_or_create_author(author_name_full)
                if author_id:
                    set_clauses.append("author_id = %s")
                    params.append(author_id)
            except Exception as e:
                print(e)

        if not set_clauses:
            return 0

        query = f"UPDATE cleaned_douban_books SET {', '.join(set_clauses)} WHERE book_id = %s"
        params.append(book_id)

        with self as dao:
            try:
                dao.cursor.execute(query, tuple(params))
                dao.connection.commit()
                return dao.cursor.rowcount
            except Exception as e:
                print(f"更新 book_id={book_id} 失败: {e}")
                dao.connection.rollback()
                raise

    def get_books_to_update(self, limit=100):
        """
        获取数据库中缺少详细信息的书籍ID。
        :param limit: 每次获取的数量，防止一次性加载过多。
        :return: 一个包含 book_id 的列表。
        """
        # with self as dao:
        #     # 查询 title 为 NULL 或者为空字符串的记录
        #     query = "SELECT book_id FROM cleaned_douban_books WHERE title IS NULL OR title = '' LIMIT %s"
        #     dao.cursor.execute(query, (limit,))
        #
        #     book_ids = [row[0] for row in dao.cursor.fetchall()]
        #     return book_ids

        with self as dao:
            try:
                # ORDER BY book_id ASC 确保了我们总是从表的“顶部”开始获取
                query = "SELECT book_id FROM cleaned_douban_books ORDER BY book_id ASC LIMIT %s"

                dao.cursor.execute(query, (limit,))

                book_ids = [row[0] for row in dao.cursor.fetchall()]
                return book_ids
            except mysql.connector.Error as err:
                print(f"DAO-get_top_book_ids: 查询时出错: {err}")
                return []