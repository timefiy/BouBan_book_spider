from pathlib import Path


def save_html_file(save_dir, file_name, content):
    dir_path = Path(save_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    full_path = dir_path / file_name

    if content is None:
        print(f"获取内容失败，无法保存文件：{full_path}")
        return

    with open(full_path, 'w', encoding='utf-8') as fp:
        print(f"{full_path} 文件已保存")
        fp.write(str(content))
