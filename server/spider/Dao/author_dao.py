import re
import mysql.connector
from .base_dao import BaseDAO

NATION_MAP = {
    '法': '法国', '美': '美国', '英': '英国', '日': '日本', '德': '德国',
    '俄': '俄罗斯', '加': '加拿大', '意': '意大利', '西': '西班牙',
    '澳': '澳大利亚', '台湾': '中国'
}


class AuthorDAO(BaseDAO):
    def __init__(self, db_config):
        super().__init__(db_config)

    def _parse_author_info(self, full_author_name):
        """
        [最终增强版] 从完整作者名中解析出国籍和规范化的姓名。
        """
        # 0. 初始拷贝和基本清理
        name = str(full_author_name).strip()
        nation = None

        bracket_pattern = r'[\[【(（](.*?)[\]】)）]'
        bracket_match = re.search(bracket_pattern, name)

        if bracket_match:
            content_in_bracket = bracket_match.group(1).strip()
            # 检查是否是国籍
            if content_in_bracket in NATION_MAP:
                nation = NATION_MAP[content_in_bracket]
                name = name.replace(bracket_match.group(0), '').strip()
            # 如果是其他内容（可能是英文别名），也先移除
            else:
                name = name.replace(bracket_match.group(0), '').strip()

        # 2. 统一标点符号
        # 将 · 和 / 都替换为 .
        name = re.sub(r'[·/]', '.', name)

        # 3. 移除点号后面的空格
        name = re.sub(r'\.\s+', '.', name)

        # 4. 移除尾随的英文别名括号
        name = re.sub(r'\s*\([A-Za-z\s\.]+\)$', '', name).strip()

        # 5. 规范化名字内部的多个空格为一个
        name = re.sub(r'\s+', ' ', name).strip()

        # 6. 智能判断国籍
        if nation is None:
            # 检查名字是否主要由英文字符、点和空格组成
            if re.fullmatch(r'^[A-Za-z\s\.]+$', name):
                nation = '未知'
            else:
                nation = '中国'

        return (name, nation)

    def get_or_create_author(self, full_author_name):
        """
        核心方法：获取或创建一个作者，并返回其 author_id。
        :param full_author_name: 带有国籍信息的完整作者名。
        :return: 作者的 author_id。
        """
        if not full_author_name:
            return None

        author_name, nation = self._parse_author_info(full_author_name)

        with self as dao:
            try:
                query_select = "SELECT author_id FROM author WHERE author_name = %s AND nation = %s"
                dao.cursor.execute(query_select, (author_name, nation))
                result = dao.cursor.fetchone()

                if result:
                    author_id = result[0]
                    print(f"作者 '{author_name}' 已存在，ID: {author_id}")
                    return author_id
                else:
                    # 作者不存在
                    print(f"新作者: '{author_name}' ({nation})，正在插入数据库...")
                    query_insert = "INSERT INTO author (author_name, nation) VALUES (%s, %s)"
                    dao.cursor.execute(query_insert, (author_name, nation))

                    author_id = dao.cursor.lastrowid
                    print(f"新作者插入成功，ID: {author_id}")

                    dao.connection.commit()

                    return author_id

            except mysql.connector.Error as err:
                print(f"AuthorDAO 操作失败: {err}")
                dao.connection.rollback()
                raise