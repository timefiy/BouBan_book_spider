import time
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup

from .tools.get_request import get_request
from ..config import DB_CONFIG
from .Dao.book_dao import BookDAO
from .Dao.comment_dao import CommentDAO


def parse_book_comments(html_content):
    """
    解析书籍评论页面的HTML，提取评论信息。
    
    :param html_content: 评论页面的HTML字符串
    :return: 评论列表，每个评论是一个字典
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'lxml')
    comments_list = []
    
    try:
        comment_items = soup.select('.comment-item')
        
        for item in comment_items:
            comment_data = {}
           
            user_element = item.select_one('.comment-info a')
            if user_element:
                comment_data['user_link'] = user_element['href']

            comment_text = item.select_one('.comment-content')
            if comment_text:
                comment_data['comment_file'] = comment_text.text.strip()
            
            rating_element = item.select_one('.rating')
            if rating_element:
                rating_class = rating_element.get('class', [])
                for cls in rating_class:
                    if cls.startswith('allstar'):
                        # 豆瓣的星级是以allstar开头，后面跟数字，如allstar50表示5星
                        star_match = re.search(r'allstar(\d+)', cls)
                        if star_match:
                            # NOTE：豆瓣的星级是按10分制的，需要除以10
                            comment_data['comment_star'] = int(star_match.group(1)) // 10
                            break
            
            # 有用数量
            votes_element = item.select_one('.vote-count')
            if votes_element:
                try:
                    comment_data['useful'] = int(votes_element.text)
                except (ValueError, TypeError):
                    comment_data['useful'] = 0
            
            time_element = item.select_one('.comment-time')
            if time_element:
                time_text = time_element.get('title', '') or time_element.text.strip()
                comment_data['comment_time'] = time_text
                
                comment_info = item.select_one('.comment-info')
                if comment_info:
                    info_text = comment_info.get_text()
                    place_match = re.search(r'\((.+?)\)', info_text)
                    if place_match:
                        comment_data['comment_place'] = place_match.group(1).strip()
            
            if comment_data: 
                comments_list.append(comment_data)
        
        return comments_list
    
    except Exception as e:
        print(f"解析评论页面时发生错误: {e}")
        return []


def crawl_book_comments(book_id, max_comments=30):
    """
    爬取指定图书的评论
    
    :param book_id: 图书ID
    :param max_comments: 最大评论数量
    :return: 评论列表
    """
    comments = []
    page = 0
    # NOTE：豆瓣每页显示20条评论
    comments_per_page = 20  
    
    while len(comments) < max_comments:
        start = page * comments_per_page
        url = f"https://book.douban.com/subject/{book_id}/comments/?start={start}&limit=20&status=P&sort=score"
        print(f"正在爬取图书 {book_id} 的评论，第 {page+1} 页: {url}")
        
        html_content = get_request(url)
        if not html_content:
            print(f"获取评论页面失败，URL: {url}")
            break
        
        page_comments = parse_book_comments(html_content)
        if not page_comments:
            print(f"未找到更多评论，停止爬取")
            break
        
        
        for comment in page_comments:
            comment['book_id'] = book_id
        
        comments.extend(page_comments)
        
        
        if len(comments) >= max_comments:
            comments = comments[:max_comments]
            break
        
        # 如果当前页评论数少于每页评论数，说明已经到达最后一页
        if len(page_comments) < comments_per_page:
            break
        
        page += 1
        time.sleep(random.uniform(0.1, 2))
    
    return comments


def crawl_multiple_books_comments(max_books=30, max_comments_per_book=30, save_to_db=False):
    """
    爬取多本图书的评论
    
    :param max_books: 最大爬取图书数量
    :param max_comments_per_book: 每本图书最大爬取评论数量
    :param save_to_db: 是否将评论保存到数据库
    """
    book_dao = BookDAO(DB_CONFIG)
    comment_dao = CommentDAO(DB_CONFIG) if save_to_db else None
    
    print(f"\n{'=' * 20} 开始爬取图书评论 {'=' * 20}")
    
    # 获取需要爬取评论的图书ID列表
    book_ids = book_dao.get_books_for_comments(limit=max_books)
    
    if not book_ids:
        print("没有找到需要爬取评论的图书！")
        return
    
    total_books = len(book_ids)
    print(f"计划爬取 {total_books} 本图书的评论，每本最多 {max_comments_per_book} 条")
    print(f"是否保存到数据库: {'是' if save_to_db else '否'}")
    
    total_comments = 0
    total_saved = 0
    
    for index, book_id in enumerate(book_ids, 1):
        print(f"\n--- 正在处理第 {index}/{total_books} 本书 (ID: {book_id}) ---")
        
        book_title = book_dao.get_book_title(book_id)
        if book_title:
            print(f"图书标题: {book_title}")
        
        book_comments = crawl_book_comments(book_id, max_comments_per_book)
        
        if book_comments:
            print(f"成功爬取 {len(book_comments)} 条评论")
            
            if save_to_db:
                try:
                    saved_count = comment_dao.add_comments(book_comments)
                    print(f"成功保存 {saved_count} 条评论到数据库")
                    total_saved += saved_count
                except Exception as e:
                    print(f"保存评论到数据库失败: {e}")
            else:
                print_comments(book_comments)
            
            total_comments += len(book_comments)
        else:
            print(f"未能获取到图书 {book_id} 的评论")
        
        if index < total_books:
            delay = random.uniform(0.1, 2)
            print(f"等待 {delay:.2f} 秒后继续...")
            time.sleep(delay)
    
    print(f"共爬取了 {total_books} 本图书的 {total_comments} 条评论")
    if save_to_db:
        print(f"成功保存 {total_saved} 条评论到数据库")


def print_comments(comments):
    """
    打印评论数量信息
    :param comments: 评论列表
    """
    print(f"共爬取到 {len(comments)} 条评论")


def crawl_comments_entry(book_id=None, max_books=30, max_comments=30, save_to_db=False):
    """
    豆瓣图书评论爬虫入口函数
    
    :param book_id: 指定要爬取评论的图书ID，如果提供则只爬取该图书的评论，否则按照评论数爬取
    :param max_books: 最大爬取图书数量，默认为30
    :param max_comments: 每本图书最大爬取评论数量，默认为30
    :param save_to_db: 是否将评论保存到数据库
    """
    if book_id:
        # 如果指定了图书ID，只爬取该图书的评论
        print(f"爬取图书ID {book_id} 的评论")
        comments = crawl_book_comments(book_id, max_comments)
        
        if comments:
            print(f"成功爬取 {len(comments)} 条评论")
            
            if save_to_db:
                comment_dao = CommentDAO(DB_CONFIG)
                try:
                    saved_count = comment_dao.add_comments(comments)
                    print(f"成功保存 {saved_count} 条评论到数据库")
                except Exception as e:
                    print(f"保存评论到数据库失败: {e}")
            else:
                print_comments(comments)
        else:
            print(f"未能获取到图书 {book_id} 的评论")
    else:
        # 爬取多本图书的评论
        crawl_multiple_books_comments(
            max_books=max_books, 
            max_comments_per_book=max_comments,
            save_to_db=save_to_db
        )


if __name__ == '__main__':
    # 默认参数
    crawl_comments_entry(book_id=None, max_books=30, max_comments=30, save_to_db=True)


