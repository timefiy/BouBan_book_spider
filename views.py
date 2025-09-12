from flask import render_template, jsonify
from server.config import DB_CONFIG
from server.spider.Dao.base_dao import BaseDAO
import mysql.connector


class AnalyticsDAO(BaseDAO):
    """数据分析相关的数据访问类"""
    def __init__(self, DB_CONFIG):
        super().__init__(DB_CONFIG)
    
    def get_authors_by_country(self):
        """获取各国作家数量统计"""
        with self as dao:
            try:
                query = """
                SELECT nation, COUNT(*) as author_count 
                FROM author 
                GROUP BY nation 
                ORDER BY author_count DESC
                """
                dao.cursor.execute(query)
                return dao.cursor.fetchall()
            except mysql.connector.Error as err:
                print(f"获取作家国籍统计失败: {err}")
                return []
    
    def get_comment_usefulness_stats(self):
        """获取评论有用数统计"""
        with self as dao:
            try:
                query = """
                SELECT 
                    useful,
                    COUNT(*) as comment_count,
                    AVG(comment_star) as avg_rating
                FROM comments 
                GROUP BY useful 
                ORDER BY useful DESC
                LIMIT 20
                """
                dao.cursor.execute(query)
                return dao.cursor.fetchall()
            except mysql.connector.Error as err:
                print(f"获取评论有用数统计失败: {err}")
                return []
    
    def get_comment_time_analysis(self):
        """分析超过1年的书评论时间分布"""
        with self as dao:
            try:
                query = """
                SELECT 
                    YEAR(c.comment_time) as comment_year,
                    MONTH(c.comment_time) as comment_month,
                    COUNT(*) as comment_count,
                    AVG(c.useful) as avg_useful
                FROM comments c
                JOIN cleaned_douban_books b ON c.book_id = b.book_id
                WHERE b.publication_year < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                AND c.comment_time IS NOT NULL
                GROUP BY YEAR(c.comment_time), MONTH(c.comment_time)
                ORDER BY comment_year DESC, comment_month DESC
                """
                dao.cursor.execute(query)
                return dao.cursor.fetchall()
            except mysql.connector.Error as err:
                print(f"获取评论时间分析失败: {err}")
                return []
    
    def get_book_length_preference(self):
        """分析读者对长篇/短篇的偏好（通过页数）"""
        with self as dao:
            try:
                query = """
                SELECT 
                    CASE 
                        WHEN page_count < 200 THEN '短篇(<200页)'
                        WHEN page_count BETWEEN 200 AND 400 THEN '中篇(200-400页)'
                        WHEN page_count > 400 THEN '长篇(>400页)'
                        ELSE '未知'
                    END as book_length,
                    COUNT(*) as book_count,
                    AVG(rating) as avg_rating,
                    AVG(rating_sum) as avg_rating_count
                FROM cleaned_douban_books 
                WHERE page_count IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN page_count < 200 THEN '短篇(<200页)'
                        WHEN page_count BETWEEN 200 AND 400 THEN '中篇(200-400页)'
                        WHEN page_count > 400 THEN '长篇(>400页)'
                        ELSE '未知'
                    END
                ORDER BY book_count DESC
                """
                dao.cursor.execute(query)
                return dao.cursor.fetchall()
            except mysql.connector.Error as err:
                print(f"获取图书长度偏好统计失败: {err}")
                return []


# 初始化数据访问对象
analytics_dao = AnalyticsDAO(DB_CONFIG)


# ==================== 页面视图函数 ====================

def index():
    """首页 - 数据分析总览"""
    return render_template('index.html')


def authors_analysis_page():
    """作家国籍分析页面"""
    return render_template('authors_analysis.html')


def comments_analysis_page():
    """评论分析页面"""
    return render_template('comments_analysis.html')


def time_analysis_page():
    """评论时间分析页面"""
    return render_template('time_analysis.html')


def length_analysis_page():
    """图书长度偏好分析页面"""
    return render_template('length_analysis.html')


# ==================== API视图函数 ====================

def authors_by_country():
    """API: 各国作家数量统计"""
    try:
        data = analytics_dao.get_authors_by_country()
        result = [{'country': row[0], 'count': row[1]} for row in data]
        return jsonify({
            'success': True,
            'data': result,
            'message': '获取作家国籍统计成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'message': f'获取作家国籍统计失败: {str(e)}'
        })


def comment_usefulness():
    """API: 图书评论有用数统计"""
    try:
        data = analytics_dao.get_comment_usefulness_stats()
        result = [{'useful': row[0], 'count': row[1], 'avg_rating': float(row[2]) if row[2] else 0} for row in data]
        return jsonify({
            'success': True,
            'data': result,
            'message': '获取评论有用数统计成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'message': f'获取评论有用数统计失败: {str(e)}'
        })


def comment_time_analysis():
    """API: 超过1年的书评论时间分析"""
    try:
        data = analytics_dao.get_comment_time_analysis()
        result = [
            {
                'year': row[0], 
                'month': row[1], 
                'count': row[2], 
                'avg_useful': float(row[3]) if row[3] else 0
            } 
            for row in data
        ]
        return jsonify({
            'success': True,
            'data': result,
            'message': '获取评论时间分析成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'message': f'获取评论时间分析失败: {str(e)}'
        })


def book_length_preference():
    """API: 读者对长篇/短篇的偏好分析"""
    try:
        data = analytics_dao.get_book_length_preference()
        result = [
            {
                'length_category': row[0],
                'book_count': row[1],
                'avg_rating': float(row[2]) if row[2] else 0,
                'avg_rating_count': float(row[3]) if row[3] else 0
            }
            for row in data
        ]
        return jsonify({
            'success': True,
            'data': result,
            'message': '获取图书长度偏好统计成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'message': f'获取图书长度偏好统计失败: {str(e)}'
        })
