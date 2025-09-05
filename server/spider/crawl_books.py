import time
import random
from bs4 import BeautifulSoup
from urllib.parse import unquote  # 导入 unquote 用于解码URL

from .Dao.book_dao import BookDAO
from .tools.get_url import get_tag_urls
from .tools.get_request import get_request
from ..config import DB_CONFIG
from .Dao.book_tag_dao import BookTagDAO # 导入新的DAO


def parse_and_save_books_from_tags():
    """
    抓取标签页面，解析书籍信息，并将书籍与标签的关联关系存入数据库。
    """
    book_tag_dao = BookTagDAO(DB_CONFIG)
    book_dao = BookDAO(DB_CONFIG)

    # 获取要处理的标签URL列表
    tag_urls = get_tag_urls(tags_num=6)

    total_relations_added = 0

    for tag_url in tag_urls:
        print(f"\n--- 正在处理分类URL: {tag_url} ---")
        tag_html = get_request(tag_url)

        if not tag_html:
            print(f"警告：请求失败，跳过URL: {tag_url}")
            continue

        tag_soup = BeautifulSoup(tag_html, 'lxml')
        try:
            tag_name = unquote(tag_url.split('/')[-1])
            print(f"当前页面的标签是: '{tag_name}'")
        except Exception:
            print(f"无法从URL中解析标{tag_url}")
            continue

        book_list_ul = tag_soup.select_one('ul.subject-list')
        if not book_list_ul:
            print(f"警告：在URL中未找到图书列表，跳过: {tag_url}")
            continue

        book_items = book_list_ul.select('li.subject-item')
        print(f"在此页面 {len(book_items)} 本书。")

        # [x]: 提取id与关系
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

        #[ ]: 向数据库中插入数据
        if relations_to_insert:
            print(f"准备将 {len(relations_to_insert)} 条数据写入数据库...")
            try:
                book_dao.ensure_books_exist(book_ids_on_page)
                inserted_count = book_tag_dao.add_book_tag_relations(relations_to_insert)
                print(f"成功插入 {inserted_count} 条新关联。")
                total_relations_added += inserted_count

            except Exception as e:
                print(f"数据库操作失败: {e}")

        time.sleep(random.uniform(1, 3))

    print(f"总共向数据库添加了 {total_relations_added} 条新的书-标签关联。")


if __name__ == '__main__':
    parse_and_save_books_from_tags()