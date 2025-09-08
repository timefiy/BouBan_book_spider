"""
从豆瓣图书标签页面解析图书标签
"""

import json
from bs4 import BeautifulSoup

from .get_tag_file import get_book_tag_file
from ..config import DB_CONFIG
from .Dao.tag_dao import TagDAO


def get_soup(markup):
    return BeautifulSoup(markup, 'lxml')


def get_book_type_dict():
    tag_file = get_book_tag_file()
    if not tag_file:
        print("未能获取到豆瓣标签页面")
        return {}
    soup = get_soup(tag_file)
    tag_dict = {}
    tag_area = soup.select_one('#content > div > div.article > div:nth-child(2)')
    if not tag_area:
        print("未能找到标签区域")
        return {}
    category_divs = tag_area.find_all('div', recursive=False)
    for category_div in category_divs:
        h2_tag = category_div.select_one('h2')
        if h2_tag:
            maintag_text = h2_tag.get_text(strip=True).split('·')[0].strip()
            sub_tags = []
            table_tag = category_div.select_one('table.tagCol')
            if table_tag:
                a_tags = table_tag.select('td > a')
                for a_tag in a_tags:
                    sub_tags.append(a_tag.get_text(strip=True))
            if maintag_text and sub_tags:
                tag_dict[maintag_text] = sub_tags
    return tag_dict


def save_tags_to_db(tag_dict):
    try:
        tag_dao = TagDAO(DB_CONFIG)

        print("正在从数据库加载已存在的标签...")
        existing_tags = tag_dao.get_existing_tags()
        print(f"加载完成！数据库中已存在 {len(existing_tags)} 个唯一标签。")

        print("开始从豆瓣解析图书标签...")
        parsed_tags = get_book_type_dict()
        if not parsed_tags:
            print("未能解析出任何数据，程序终止。")
            return

        print("正在筛选新标签...")
        new_tags_to_insert = []
        for main_tag, sub_tags in parsed_tags.items():
            for tag in sub_tags:
                if tag not in existing_tags:
                    new_tags_to_insert.append((main_tag, tag))
                    existing_tags.add(tag)

        if new_tags_to_insert:
            print(f"发现 {len(new_tags_to_insert)} 个新标签，准备写入数据库...")
            inserted_count = tag_dao.add_new_tags(new_tags_to_insert)
            print(f"操作成功！共向数据库插入了 {inserted_count} 条新记录。")
        else:
            print("没有发现任何新标签，数据库无需更新。")

    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == '__main__':

    print("开始从豆瓣解析图书标签...")
    parsed_tags = get_book_type_dict()

    if parsed_tags:
        print("解析完成，数据如下:")
        # ident = 4:缩进4格子
        # ensure_ascii=False： 允许使用非ascill字符
        print(json.dumps(parsed_tags, indent=4, ensure_ascii=False))

        save_tags_to_db(parsed_tags, DB_CONFIG)
    else:
        print("未能解析出任何数据，程序终止。")