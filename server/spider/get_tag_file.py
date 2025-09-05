from pathlib import Path

from .tools.get_request import get_request
from .tools.save_file import save_html_file


def download_book_tag():
    try:
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
    except NameError:
        #  选取当前的目录
        BASE_DIR = Path.cwd()

    # 这里 save_dir 是一个 Path 对象
    save_dir = BASE_DIR / "static"
    file_name = 'douban_book_all_tag.html'

    book_tag_url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
    tag_file_path = save_dir / file_name

    if tag_file_path.exists() and tag_file_path.is_file():
        print(f'文件 {tag_file_path} 已存在')
    else:
        print(f'文件 {tag_file_path} 不存在，正在下载')
        html_content = get_request(book_tag_url)
        save_html_file(save_dir=save_dir, file_name=file_name, content=html_content)


def get_book_tag_file():
    book_tag_url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
    html_content = get_request(book_tag_url)
    return html_content


if __name__ == '__main__':
    download_book_tag()