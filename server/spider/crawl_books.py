"""
@author: timefiy
爬取豆瓣图书标签页面，解析书籍信息，并将书籍与标签的关联关系存入数据库。
规定crawl_detail_book.py爬取那些书籍
只能通过标签页面查询，且需要按照tag库（从后往前）的顺序进行爬取
"""

import time
import random
from bs4 import BeautifulSoup
from urllib.parse import unquote  # 导入 unquote 用于解码URL

from .Dao.book_dao import BookDAO
from .tools.get_url import get_tag_urls
from .tools.get_request import get_request
from ..config import DB_CONFIG
from .Dao.book_tag_dao import BookTagDAO # 导入新的DAO


def parse_and_save_books_from_tags(max_books=30):
    """
    抓取标签页面，解析书籍信息，并将书籍与标签的关联关系存入数据库。
    :param max_books: 每个标签最多抓取的书籍数量，默认为30
    :type max_books: int
    """
    book_tag_dao = BookTagDAO(DB_CONFIG)
    book_dao = BookDAO(DB_CONFIG)

    # 获取要处理的标签URL列表
    tag_urls = get_tag_urls(tags_num=6)

    total_relations_added = 0

    # 爬取当前的页面的标签名称
    for base_tag_url in tag_urls:
        print(f"\n--- 正在处理标签: {base_tag_url} ---")
        
        # 解析标签名称
        try:
            tag_name = unquote(base_tag_url.split('/')[-1])
            print(f"当前处理的标签是: '{tag_name}'")
        except Exception:
            print(f"无法从URL中解析标签: {base_tag_url}")
            continue
            
        # 初始化计数和页码
        books_processed = 0
        current_page = 0
        books_per_page = 20  # 豆瓣每页显示20本书
        
        # 循环处理每一页，直到达到最大书籍数或没有更多页面
        while books_processed < max_books:
            # 构建当前页的URL
            page_start = current_page * books_per_page
            current_url = f"{base_tag_url}?start={page_start}" if page_start > 0 else base_tag_url
            
            print(f"\n--- 正在处理页面: {current_url} ---")
            tag_html = get_request(current_url)
            
            if not tag_html:
                print(f"警告：请求失败，跳过URL: {current_url}")
                break  # 请求失败，结束此标签的处理
                
            tag_soup = BeautifulSoup(tag_html, 'lxml')
            
            book_list_ul = tag_soup.select_one('ul.subject-list')
            if not book_list_ul:
                print(f"警告：在URL中未找到图书列表，跳过: {current_url}")
                break  # 没有找到书籍列表，结束此标签的处理
                
            book_items = book_list_ul.select('li.subject-item')
            if not book_items:
                print(f"当前页面没有找到书籍，可能已到达最后一页")
                break  # 没有更多书籍，结束此标签的处理
                
            print(f"在此页面找到 {len(book_items)} 本书。")

            # [x]提取该tag下的图书的id
            book_ids_on_page = []
            relations_to_insert = []
            for item in book_items:
                book_link_element = item.select_one('h2 > a')
                if book_link_element and 'subject' in book_link_element['href']:
                    book_id_str = book_link_element['href'].split('/')[-2]
                    try:
                        book_id = int(book_id_str)
                        book_ids_on_page.append(book_id)
                        relations_to_insert.append((book_id, tag_name))
                    except (ValueError, IndexError):
                        print(f"警告：无法从链接 {book_link_element['href']} 中解析出 book_id")

            # [x]向数据库中插入数据
            if relations_to_insert:
                print(f"准备将 {len(relations_to_insert)} 条数据写入数据库...")
                try:
                    book_dao.ensure_books_exist(book_ids_on_page)
                    inserted_count = book_tag_dao.add_book_tag_relations(relations_to_insert)
                    print(f"成功插入 {inserted_count} 条新关联。")
                    total_relations_added += inserted_count
                    books_processed += len(relations_to_insert)
                    print(f"当前标签已处理 {books_processed}/{max_books} 本书")

                except Exception as e:
                    print(f"数据库操作失败: {e}")
                    
            # 准备下一页
            current_page += 1
            
            # 如果已经达到或超过最大书籍数，结束循环
            if books_processed >= max_books:
                print(f"已达到最大书籍数量限制 ({max_books})，停止抓取此标签")
                break
                
            # 延时请求
            time.sleep(random.uniform(0.1, 1.5))

    print(f"总共向数据库添加了 {total_relations_added} 条新的书-标签关联。")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='抓取豆瓣图书标签页面并保存到数据库')
    parser.add_argument('--max-books', type=int, default=30, 
                        help='每个标签最多抓取的书籍数量，默认为30')
    args = parser.parse_args()
    
    parse_and_save_books_from_tags(max_books=args.max_books)