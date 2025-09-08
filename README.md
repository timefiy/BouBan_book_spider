# 豆瓣图书爬虫项目

这是一个用 Python 开发的豆瓣图书数据爬虫项目，能够自动抓取豆瓣网站上的图书信息、标签、评分、用户评论等数据，并存储到 MySQL 数据库中。

## 项目功能

- 📚 抓取豆瓣图书标签分类
- 🔍 根据标签抓取相关图书信息（支持翻页）
- 📖 抓取图书详细信息（作者、出版社、评分、ISBN等）
- 💬 抓取图书用户评论和评分
- 💾 将数据保存到 MySQL 数据库
- 🔄 支持断点续爬和去重功能
- ⚙️ 可配置爬取数量和频率控制

## 技术栈

- **Python 3.x** - 主要开发语言
- **Flask** - Web框架
- **BeautifulSoup4** - HTML解析
- **MySQL** - 数据存储
- **mysql-connector-python** - MySQL数据库连接
- **requests** - HTTP请求处理
- **lxml** - XML/HTML解析器
- **random & time** - 请求频率控制

## 项目结构

```
DouBan/
├── app.py                          # Flask应用入口
├── README.md                       # 项目说明文档
├── requirements.txt                # Python依赖包列表
├── .gitignore                     # Git忽略文件配置
├── server/                        # 服务器端代码
│   ├── __init__.py
│   ├── app.py                     # 服务器应用逻辑
│   ├── config.py                  # 数据库配置文件
│   ├── config.py.example          # 配置文件模板
│   └── spider/                    # 爬虫模块
│       ├── __init__.py
│       ├── crawl_books.py         # 爬取图书列表（支持翻页）
│       ├── crawl_detail_book.py   # 爬取图书详情
│       ├── crawl_comments.py      # 爬取图书评论
│       ├── get_tag_file.py        # 获取标签文件
│       ├── save_tag_for_db.py     # 保存标签到数据库
│       ├── Dao/                   # 数据访问对象层
│       │   ├── __init__.py
│       │   ├── base_dao.py        # 基础数据访问类
│       │   ├── author_dao.py      # 作者数据访问
│       │   ├── book_dao.py        # 图书数据访问
│       │   ├── book_tag_dao.py    # 图书标签关联数据访问
│       │   ├── comment_dao.py     # 评论数据访问
│       │   └── tag_dao.py         # 标签数据访问
│       └── tools/                 # 工具类
│           ├── __init__.py
│           ├── get_request.py     # HTTP请求处理
│           ├── get_url.py         # URL生成工具
│           └── save_file.py       # 文件保存工具
├── sql/                           # 数据库脚本
│   └── douban.sql                 # 数据库表结构
├── static/                        # 静态资源
│   ├── douban_book_all_tag.html   # 豆瓣图书标签HTML
│   └── html/                      # HTML文件存储
└── templates/                     # Flask模板文件
```

## 数据库设计

项目使用MySQL数据库，主要包含以下表结构：

### 核心表结构

- **`cleaned_douban_books`** - 图书主表
  - 存储图书基本信息（标题、ISBN、评分、价格等）
  - 包含详细的评分分布数据（1-5星比例）
  
- **`author`** - 作者表
  - 存储作者信息（姓名、国籍）
  
- **`tags`** - 标签表  
  - 存储图书分类标签
  
- **`book_tag`** - 图书标签关联表
  - 图书与标签的多对多关系
  
- **`comments`** - 评论表
  - 存储用户评论内容、评分、时间等
  - 包含评论有用数统计

### 约束和特性

- 外键约束确保数据完整性
- 评分字段有检查约束（1-5星）
- 支持级联删除和更新
- UTF8MB4字符集支持emoji和特殊字符

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

#### 基础爬虫流程

1. **抓取标签数据**
```bash
python -m server.spider.get_tag_file
```

2. **保存标签到数据库**
```bash
python -m server.spider.save_tag_for_db
```

3. **根据标签抓取图书列表**（支持翻页和数量控制）
```bash
python -m server.spider.crawl_books
```

4. **抓取图书详细信息**
```bash
python -m server.spider.crawl_detail_book
```

5. **抓取图书评论**
```bash
python -m server.spider.crawl_comments
```

#### 高级功能

**自定义爬取参数：**

- 修改 `crawl_books.py` 中的 `main()` 函数参数
- 修改 `crawl_comments.py` 中的 `crawl_comments_entry()` 函数参数

**参数说明：**
- `max_books`: 最大爬取图书数量
- `max_comments`: 每本图书最大爬取评论数量  
- `save_to_db`: 是否保存到数据库
- `book_id`: 指定爬取特定图书的评论

#### Web应用
```bash
python app.py
```

## 项目特色

- 🚀 **模块化设计** - 采用DAO模式，代码结构清晰
- 🛡️ **数据完整性** - 完善的数据库约束和错误处理
- 🔄 **智能去重** - 使用 INSERT IGNORE 避免重复数据
- ⏱️ **频率控制** - 内置随机延时，避免请求过于频繁
- 📊 **丰富数据** - 包含图书详情、评分分布、用户评论等
- 🔧 **易于扩展** - 清晰的代码结构，便于添加新功能

## 注意事项

- ⚠️ 请合理控制爬取频率，避免对豆瓣服务器造成过大压力
- 📚 本项目仅供学习和研究使用，请勿用于商业用途
- 🤖 遵守豆瓣网站的robots.txt规则
- 🔒 数据库配置文件包含敏感信息，请勿提交到公共仓库
- 🐛 如遇到评分约束错误，程序会自动设置默认评分

## 常见问题

**Q: 数据库插入失败，提示约束违反？**
A: 通常是评分字段超出1-5范围，程序已自动处理此问题。

**Q: 如何修改爬取数量？**
A: 修改对应爬虫文件中的函数参数，如 `max_books=50`。

**Q: 爬虫运行很慢？**
A: 这是正常现象，程序内置了延时机制保护目标服务器。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
