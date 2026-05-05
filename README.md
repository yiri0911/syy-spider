# syy-spider
# Book Scraper - 静态图书信息爬虫

这是一个简单的 Python 网络爬虫项目，用于从 **books.toscrape.com**（一个专门用于爬虫练习的静态图书网站）抓取第一页的图书信息，并将结果保存为 CSV 文件。

## 功能特性

- 抓取第一页（共 20 本）图书的：
  - 书名
  - 价格（英镑）
  - 评价星级（例如 “Three” 转换为 3 星）
  - 是否有库存
- 使用 `requests` + `BeautifulSoup` 进行静态页面解析
- 设置 `User-Agent` 请求头，模拟浏览器访问
- 内置简单的请求重试机制（最多重试 3 次，间隔 1 秒）
- 完善的异常处理和代码注释
- 输出结果为 `books.csv`，包含标准列头

## 项目结构
├── book_scraper.py # 主爬虫脚本

├── books.csv # 运行后生成的 CSV 文件（自动创建）

### 环境要求

- Python 3.6 或更高版本
- 需要安装以下 Python 库：
  - `requests`
  - `beautifulsoup4`

### 安装依赖

```bash
pip install requests beautifulsoup4
```
执行成功后，会在当前目录下生成 books.csv 文件，你可以用 Excel、文本编辑器或 pandas 等工具打开查看。

# 代码核心逻辑说明

## 1. 发送 HTTP 请求
使用 `requests.get()` 并携带自定义 `User-Agent` 头，同时设置超时和重试机制。

## 2. 解析 HTML
利用 `BeautifulSoup` 定位图书列表区域（`<ol class="row">` 下的所有 `<li>` 元素）。

## 3. 提取数据
- 书名：从 `h3 > a` 标签的 `title` 属性获取  
- 价格：从 `p.price_color` 标签获取文本并去除货币符号  
- 星级：从 `p.star-rating` 的 `class` 名称（如 `Three`）转换为数字 3  
- 库存：从产品页面的 `p.instock` 类别判断（也可直接使用列表页的部分信息，本脚本从产品页提取更准确）

## 4. 保存 CSV
使用 Python 内置的 `csv` 模块将数据写入文件，编码为 `utf-8-sig` 以确保 Excel 正常打开。

---

# 自定义爬取数量

脚本支持通过修改代码顶部的 `MAX_BOOKS` 变量来设置最大爬取数量。默认值为 `20`（只爬取第一页）。  
若需爬取更多书籍，请按以下步骤操作：

1. 打开 `book_scraper.py`  
2. 找到变量 `MAX_BOOKS = 20`  
3. 将数字改为你需要的数量（例如 `50`）  
4. 保存文件并重新运行脚本  

> **注意**：该网站每页最多显示 20 本书。如果需要爬取超过 20 本，脚本会自动遍历后续页码，直到爬够指定数量或没有更多书籍。  
> 建议设置合理的延迟（`time.sleep(1)`）并遵守网站的 `robots.txt` 规则。

---

# 注意事项
- 本爬虫仅用于学习和练习，请遵守 `robots.txt` 协议（该示例网站允许爬虫练习）。  
- 如果需要抓取其他网站，请修改 `START_URL` 和解析规则，并注意目标网站的合规性。  
- 不建议高频率发送请求，代码中已内置 `time.sleep(1)` 避免对服务器造成压力。
