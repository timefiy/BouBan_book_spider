from urllib.parse import quote

from ..Dao.tag_dao import TagDAO
from ...config import DB_CONFIG

def get_tag_urls(tags_num = 5, **kwargs):
    tag_urls = []
    tag_num_now = 0
    base_url = "https://book.douban.com/tag/"

    tag_dao = TagDAO(DB_CONFIG)

    print("获取标签中")
    tags = tag_dao.get_tags(limit=tags_num)
    for tag in tags:
        if tag_num_now < tags_num:
            encoded_tag = quote(tag)
            tag_url = f"{base_url}{encoded_tag}"
            tag_urls.append(tag_url)
            tag_num_now += 1
        else:
            break

    return tag_urls

if __name__ == "__main__":
    get_tag_urls()