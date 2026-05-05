#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络爬虫脚本（增强版） - 爬取 http://books.toscrape.com/ 上的图书信息
功能：支持自定义爬取数量，自动翻页，输出到 CSV 文件
"""

import csv
import time
import re
import argparse
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ==================== 配置参数 ====================
BASE_URL = "http://books.toscrape.com/"
START_URL = "http://books.toscrape.com/"           # 起始页面（第一页）
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/120.0.0.0 Safari/537.36")
TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1

# 星级映射表
STAR_MAPPING = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}


# ==================== 辅助函数 ====================
def fetch_html(url, max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """带重试的页面获取函数"""
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"请求失败 ({attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return None


def parse_books_from_page(html):
    """
    从一页的 HTML 中解析出所有图书信息
    返回: list of dict, 每个 dict 包含 name, price, star, in_stock
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []
    book_cards = soup.select("li.col-xs-6.col-sm-4.col-md-3.col-lg-3")

    for card in book_cards:
        # 书名
        name_tag = card.select_one("h3 a")
        name = name_tag.get("title", "").strip() if name_tag else "Unknown"

        # 价格
        price_elem = card.select_one("p.price_color")
        price = price_elem.text.strip().replace("£", "") if price_elem else "0.00"

        # 星级
        rating_elem = card.select_one("p.star-rating")
        star_text = "Zero"
        if rating_elem:
            classes = rating_elem.get("class", [])
            star_class = [c for c in classes if c in STAR_MAPPING]
            star_text = star_class[0] if star_class else "Zero"
        star_num = STAR_MAPPING.get(star_text, 0)

        # 库存
        stock_elem = card.select_one("p.instock.availability")
        in_stock = False
        if stock_elem:
            stock_text = stock_elem.text.strip()
            in_stock = "In stock" in stock_text

        books.append({
            "name": name,
            "price": price,
            "star": star_num,
            "in_stock": in_stock
        })
    return books


def get_next_page_url(html, current_url):
    """
    从当前页 HTML 中提取下一页的链接，并转换为绝对 URL
    如果没有下一页，返回 None
    """
    soup = BeautifulSoup(html, "html.parser")
    next_li = soup.find("li", class_="next")
    if next_li:
        next_a = next_li.find("a")
        if next_a and next_a.get("href"):
            next_rel_url = next_a["href"]
            return urljoin(current_url, next_rel_url)
    return None


def save_to_csv(books_data, filename="books.csv"):
    """保存数据到 CSV 文件"""
    if not books_data:
        print("没有数据可保存")
        return
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["书名", "价格(£)", "星级", "是否有库存"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book in books_data:
            writer.writerow({
                "书名": book["name"],
                "价格(£)": book["price"],
                "星级": book["star"],
                "是否有库存": "是" if book["in_stock"] else "否"
            })
    print(f"已保存 {len(books_data)} 条数据到 {filename}")


# ==================== 主爬虫 ====================
def crawl_books(limit=20, output="books.csv"):
    """
    爬取指定数量的图书（自动翻页）
    :param limit: 期望爬取的书籍数量
    :param output: 输出 CSV 文件名
    """
    print(f"开始爬取，目标数量: {limit} 本")
    all_books = []
    current_url = START_URL

    while len(all_books) < limit and current_url:
        print(f"正在抓取: {current_url}")
        html = fetch_html(current_url)
        if not html:
            print(f"抓取失败，跳过: {current_url}")
            break

        page_books = parse_books_from_page(html)
        if not page_books:
            print("当前页无书籍，终止爬取")
            break

        # 计算需要从本页取多少本书（避免超出限量）
        need = limit - len(all_books)
        all_books.extend(page_books[:need])
        print(f"  本页获得 {len(page_books)} 本书，累计 {len(all_books)} 本")

        # 如果还没达到数量，获取下一页链接
        if len(all_books) < limit:
            current_url = get_next_page_url(html, current_url)
        else:
            break

    # 处理未达到目标的情况
    if len(all_books) < limit:
        print(f"警告：总共只有 {len(all_books)} 本书，无法达到目标 {limit} 本")

    # 数据预览
    print("\n数据预览（前5条）：")
    for i, book in enumerate(all_books[:5], 1):
        print(f"{i}. {book['name']} | £{book['price']} | {book['star']}星 | {'有库存' if book['in_stock'] else '无库存'}")

    save_to_csv(all_books, output)
    return all_books


# ==================== 命令行入口 ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="爬取 books.toscrape.com 的图书信息")
    parser.add_argument("-n", "--num", type=int, default=20,
                        help="要爬取的书籍数量，默认 20 本")
    parser.add_argument("-o", "--output", type=str, default="books.csv",
                        help="输出 CSV 文件名，默认 books.csv")
    args = parser.parse_args()

    crawl_books(limit=args.num, output=args.output)