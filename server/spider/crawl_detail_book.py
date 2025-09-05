import time
import random
import re
import mysql.connector
from bs4 import BeautifulSoup

from .tools.get_request import get_request
from ..config import DB_CONFIG
from .Dao.book_dao import BookDAO


def parse_book_detail(html_content):
    """
    解析书籍详情页的HTML，提取所有关键信息。
    :param html_content: 详情页的HTML字符串。
    :return: 一个包含书籍所有信息的字典，如果解析失败则返回 None。
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'lxml')
    book_data = {}

    try:
        info_div = soup.select_one('#info')
        if not info_div:
            print("未找到 #info 区域")
            return None

        def get_text_after_pl(pl_text):
            element = info_div.find('span', class_='pl', string=re.compile(pl_text))
            if element:
                content = element.next_sibling
                return content.strip() if content and content.strip() else None
            return None

        def get_link_after_pl(pl_text):
            element = info_div.find('span', class_='pl', string=re.compile(pl_text))
            if element and element.find_next_sibling('a'):
                return element.find_next_sibling('a').text.strip()
            return None

        #[x]解析基本信息
        book_data['title'] = soup.select_one('h1 > span').text.strip()
        book_data['img_src'] = soup.select_one('#mainpic .nbg > img')['src'] if soup.select_one(
            '#mainpic .nbg > img') else None

        #[ ] 作者名字与id的逻辑处理问题
        book_data['author_name'] = get_link_after_pl('作者')  # 假设先存作者名
        book_data['publisher'] = get_link_after_pl('出版社')
        book_data['producer'] = get_link_after_pl('出品方')
        book_data['original_title'] = get_text_after_pl('原作名')
        book_data['translator'] = get_link_after_pl('译者')
        book_data['publication_year'] = get_text_after_pl('出版年')
        book_data['page_count'] = get_text_after_pl('页数')
        book_data['price'] = get_text_after_pl('定价')
        book_data['binding'] = get_text_after_pl('装帧')
        book_data['series'] = get_link_after_pl('丛书')
        book_data['isbn'] = get_text_after_pl('ISBN')

        #[x]解析评分信息
        rating_div = soup.select_one('#interest_sectl')
        if rating_div:
            rating_element = rating_div.select_one('strong.rating_num')
            # 清楚首尾的空白字符
            rating_text = rating_element.text.strip() if rating_element else ""
            book_data['rating'] = rating_text if rating_text else None

            rating_sum_element = rating_div.select_one('.rating_people span')
            rating_sum_text = rating_sum_element.text.strip() if rating_sum_element else ""
            book_data['rating_sum'] = rating_sum_text if rating_sum_text else None

            for i in range(5, 0, -1):
                star_element = rating_div.select_one(f'.stars{i} ~ .rating_per')
                book_data[f'stars{i}_starstop'] = star_element.text.strip() if star_element else None
        # [x]:数据清洗
        if book_data.get('page_count'):
            page_match = re.search(r'\d+', str(book_data['page_count']))
            book_data['page_count'] = int(page_match.group()) if page_match else None

        if book_data.get('price'):
            price_match = re.search(r'[\d\.]+', str(book_data['price']))
            book_data['price'] = float(price_match.group()) if price_match else None

        if book_data.get('rating'):
            try:
                book_data['rating'] = float(book_data['rating'])
            except (ValueError, TypeError):
                book_data['rating'] = None

        if book_data.get('rating_sum'):
            rating_sum_match = re.search(r'\d+', str(book_data['rating_sum']))
            book_data['rating_sum'] = int(rating_sum_match.group()) if rating_sum_match else None
        #评分部分
        for i in range(5, 0, -1):
            key = f'stars{i}_starstop'
            if book_data.get(key):
                try:
                    book_data[key] = float(book_data[key].replace('%', ''))
                except (ValueError, TypeError):
                    book_data[key] = None

        pub_year_str = book_data.get('publication_year')
        if pub_year_str:
            match = re.match(r'(\d{4})[^\d]?(\d{1,2})?', pub_year_str)
            if match:
                year = match.group(1)
                month = match.group(2)

                if month:
                    book_data['publication_year'] = f"{year}-{int(month):02d}-01"
                else:
                    book_data['publication_year'] = f"{year}-01-01"
            else:
                book_data['publication_year'] = None

        return book_data

    except Exception as e:
        print(f"解析页面时发生严重错误: {e}")
        return None


def supplement_book_details():
    book_dao = BookDAO(DB_CONFIG)

    total_books_updated = 0

    print(f"\n{'=' * 20} 开始详情补充任务 {'=' * 20}")

    book_ids_to_update = book_dao.get_books_to_update(limit=100)

    if not book_ids_to_update:
        print("数据库中所有书籍的详情都已是完整的！程序结束。")
        return

    total_count = len(book_ids_to_update)
    print(f"任务目标：需要为 {total_count} 本书补充详细信息。")

    for index, book_id in enumerate(book_ids_to_update, 1):
        print(f"\n--- 正在处理第 {index}/{total_count} 本书 (ID: {book_id}) ---")
        detail_url = f"https://book.douban.com/subject/{book_id}/"
        print(f"正在爬取: {detail_url}")
        detail_html = get_request(detail_url)

        book_details = parse_book_detail(detail_html)

        if book_details:
            try:
                print(f"正在更新 book_id={book_id} 的信息...")
                updated_count = book_dao.update_book_details(book_id, book_details)
                if updated_count > 0:
                    total_books_updated += 1
                    print(f"更新成功！")
            except mysql.connector.Error as err:
                print(f"更新 book_id={book_id} 时数据库失败: {err}")
        else:
            print(f"解析 book_id={book_id} 的详情页失败。")

        time.sleep(random.uniform(1.5, 3))

    print(f"\n{'=' * 25} 任务总结 {'=' * 25}")
    print(f"详情补充任务全部完成！")
    print(f"总共更新了 {total_books_updated} 本书的详细信息。")


if __name__ == '__main__':
    supplement_book_details()

