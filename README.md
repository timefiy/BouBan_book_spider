# 豆瓣图书爬虫项目

这是一个用 Python 开发的豆瓣图书数据爬虫项目，能够自动抓取豆瓣网站上的图书信息、标签、评分等数据，并存储到 MySQL 数据库中。

## 项目功能

- 抓取豆瓣图书标签分类
- 根据标签抓取相关图书信息
- 抓取图书详细信息（作者、出版社、评分等）
- 将数据保存到 MySQL 数据库
- 支持断点续爬和去重功能

## 技术栈

- Python 3.x
- Flask (Web框架)
- BeautifulSoup4 (HTML解析)
- MySQL (数据存储)
- 其他依赖库: requests, lxml 等

## 项目结构

```
DouBan/
├── app.py                  # Flask应用入口
├── server/                 # 服务器端代码
│   ├── __init__.py
│   ├── app.py              # 服务器应用逻辑
│   ├── config.py           # 配置文件
│   └── spider/             # 爬虫模块
│       ├── __init__.py
│       ├── crawl_books.py          # 爬取图书列表
│       ├── crawl_detail_book.py    # 爬取图书详情
│       ├── get_tag_file.py         # 获取标签文件
│       ├── save_tag_for_db.py      # 保存标签到数据库
│       ├── Dao/                    # 数据访问对象
│       │   ├── __init__.py
│       │   ├── author_dao.py       # 作者数据访问
│       │   ├── base_dao.py         # 基础数据访问类
│       │   ├── book_dao.py         # 图书数据访问
│       │   ├── book_tag_dao.py     # 图书标签关联数据访问
│       │   └── tag_dao.py          # 标签数据访问
│       └── tools/                  # 工具类
│           ├── __init__.py
│           ├── get_request.py      # 请求处理
│           ├── get_url.py          # URL生成
│           └── save_file.py        # 文件保存
├── sql/                    # SQL脚本
├── static/                 # 静态资源
│   ├── douban_book_all_tag.html    # 豆瓣图书标签HTML
│   └── html/               # HTML文件
└── templates/              # 模板文件
```

## 数据库设计

项目使用MySQL数据库，主要包含以下表结构：

- `books`: 存储图书基本信息
- `authors`: 存储作者信息
- `tags`: 存储标签信息
- `book_tag`: 图书与标签的多对多关联表

## 安装与使用

### 前置条件

- Python 3.x
- MySQL 数据库

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/douban-book-crawler.git
cd douban-book-crawler
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
编辑 `server/config.py` 文件，修改数据库连接信息：
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'douban',
    'charset': 'utf8mb4'
}
```

4. 创建数据库表结构
```bash
# 导入sql目录下的SQL脚本到MySQL
```

### 使用方法

1. 抓取标签数据
```bash
python -m server.spider.get_tag_file
```

2. 保存标签到数据库
```bash
python -m server.spider.save_tag_for_db
```

3. 根据标签抓取图书列表
```bash
python -m server.spider.crawl_books
```

4. 抓取图书详情
```bash
python -m server.spider.crawl_detail_book
```

5. 启动Web应用
```bash
python app.py
```

## 注意事项

- 请合理控制爬取频率，避免对豆瓣服务器造成过大压力
- 本项目仅供学习和研究使用，请勿用于商业用途
- 遵守豆瓣网站的robots.txt规则

## 许可证

MIT
