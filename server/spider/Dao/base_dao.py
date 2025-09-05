import mysql.connector


class BaseDAO(object):
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.db_config)
        self.cursor = self.connection.cursor()
        return self # 将 cursor 对象传递给 'as' 子句

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()

        return False