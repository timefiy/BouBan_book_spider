"""
评论数据操作类
包含：
1. 向 comments 表中批量插入评论数据
2. 获取指定图书的评论数量
"""

from .base_dao import BaseDAO
import mysql.connector
from datetime import datetime


class CommentDAO(BaseDAO):
    def __init__(self, db_config):
        super().__init__(db_config)
    
    def add_comments(self, comments):
        """
        向 comments 表中批量插入评论数据。
        
        :param comments: 评论列表，每个评论是一个字典
        :return: 插入的评论数量
        """
        if not comments:
            return 0
        
        with self as dao:
            try:
                query = """
                INSERT INTO comments 
                (book_id, user_link, comment_file, comment_star, useful, comment_time, comment_place) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                data_to_insert = []
                for comment in comments:
                    comment_time = comment.get('comment_time')
                    if comment_time:
                        try:
                            parsed_time = datetime.strptime(comment_time, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                # 尝试解析其他可能的格式
                                parsed_time = datetime.strptime(comment_time, '%Y-%m-%d')
                            except ValueError:
                                parsed_time = datetime.now()
                    else:
                        parsed_time = datetime.now()
                    
                    # 处理评分，确保在1-5范围内
                    star_rating = comment.get('comment_star', 0)
                    if not star_rating or not (1 <= star_rating <= 5):
                        star_rating = 3  #NOTE: 评论的评分默认是中性评分（3星）
                    
                    # 组装数据
                    data_to_insert.append((
                        comment.get('book_id'),
                        comment.get('user_link', ''),
                        comment.get('comment_file', ''),
                        star_rating,
                        comment.get('useful', 0),
                        parsed_time,
                        comment.get('comment_place', None)
                    ))
                
                dao.cursor.executemany(query, data_to_insert)
                
                dao.connection.commit()
                
                return dao.cursor.rowcount
            except mysql.connector.Error as err:
                print(f"CommentDAO 插入失败: {err}")
                # 回滚事务
                dao.connection.rollback()
                raise
    
    # REVIEW：这个函数是不是没有用？
    # def get_comments_count_by_book(self, book_id):
    #     """
    #     获取指定图书的评论数量。
    #     :param book_id: 图书ID
    #     :return: 评论数量
    #     """
    #     with self as dao:
    #         try:
    #             query = "SELECT COUNT(*) FROM comments WHERE book_id = %s"
    #             dao.cursor.execute(query, (book_id,))
    #             result = dao.cursor.fetchone()
    #             return result[0] if result else 0
    #         except mysql.connector.Error as err:
    #             print(f"获取图书评论数量失败: {err}")
    #             return 0
