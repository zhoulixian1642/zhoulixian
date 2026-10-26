# -*- coding: utf: utf-8 -*-
"""
book_manager.py
图书管理模块：图书增删改查、条件检索、评分排行。
"""

from mongodb_connect import get_db


class BookManager:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.books

    # ---------- 添加 ----------
    def add_book(self, book_dict):
        """添加一本图书，返回插入结果。"""
        result = self.col.insert_one(book_dict)
        return f"✅ 已添加图书，_id: {result.inserted_id}"

    def add_books_batch(self, book_list):
        """批量添加图书，返回插入条数。"""
        result = self.col.insert_many(book_list)
        return f"✅ 批量添加完成，共插入 {len(result.inserted_ids)} 本"

    # ---------- 查询 ----------
    def find_by_isbn(self, isbn):
        """按 ISBN 精确查找单本图书。"""
        book = self.col.find_one({"isbn": isbn})
        if not book:
            return "⚠️ 未找到该 ISBN 的图书"
        return self._format_book(book)

    def search_by_title(self, keyword):
        """按书名模糊搜索（包含关键词即可）。"""
        cursor = self.col.find({"title": {"$regex": keyword}})
        books = list(cursor)
        if not books:
            return f"⚠️ 书名包含「{keyword}」的图书未找到"
        return self._format_books_list(books)

    def filter_books(self, min_price=None, max_price=None,
                     category=None, min_rating=None, publisher=None):
        """多条件组合筛选图书。"""
        query = {}
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price
        if category:
            query["category"] = category
        if min_rating is not None:
            query["rating"] = {"$gte": min_rating}
        if publisher:
            query["publisher"] = publisher

        cursor = self.col.find(query)
        books = list(cursor)
        if not books:
            return "⚠️ 没有符合条件的图书"
        return self._format_books_list(books)

    def top_rated(self, n=5):
        """按评分降序取前 n 本。"""
        cursor = self.col.find().sort("rating", -1).limit(n)
        books = list(cursor)
        return f"📊 评分最高的前 {n} 本：\n" + self._format_books_list(books)

    def top_borrowed(self, n=5):
        """按借阅次数降序取前 n 本。"""
        cursor = self.col.find().sort("borrow_count", -1).limit(n)
        books = list(cursor)
        return f"📊 借阅次数最多的前 {n} 本：\n" + self._format_books_list(books)

    # ---------- 更新 ----------
    def update_stock(self, isbn, delta):
        """增减库存，delta 为正数加、负数减。"""
        result = self.col.update_one(
            {"isbn": isbn},
            {"$inc": {"stock": delta}}
        )
        if result.matched_count == 0:
            return "⚠️ 未找到该图书"
        return f"✅ 库存已调整，受影响文档数: {result.modified_count}"

    def update_price_by_category(self, category, ratio):
        """某类别所有图书价格按比例调整（如 0.9 表示打 9 折）。"""
        result = self.col.update_many(
            {"category": category},
            {"$mul": {"price": ratio}}
        )
        return f"✅ {category}类图书价格已调整，共更新 {result.modified_count} 本"

    def update_book_info(self, isbn, **kwargs):
        """更新图书的任意字段，传入键值对即可。"""
        result = self.col.update_one(
            {"isbn": isbn},
            {"$set": kwargs}
        )
        if result.matched_count == 0:
            return "⚠️ 未找到该图书"
        return f"✅ 图书信息已更新，受影响文档数: {result.modified_count}"

    # ---------- 删除 ----------
    def delete_book(self, isbn):
        """按 ISBN 删除一本图书。"""
        result = self.col.delete_one({"isbn": isbn})
        if result.deleted_count == 0:
            return "⚠️ 未找到该图书"
        return f"✅ 图书已删除，删除文档数: {result.deleted_count}"

    def delete_books_by_category(self, category):
        """删除某类别所有图书。"""
        result = self.col.delete_many({"category": category})
        return f"✅ 已删除 {category} 类图书，共删除 {result.deleted_count} 本"

    # ---------- 格式化输出 ----------
    def _format_book(self, book):
        """单本图书格式化字符串。"""
        tags = "、".join(book.get("tags", [])) or "无标签"
        return (
            f"📖 {book.get('title', '未知')}\n"
            f"   ISBN: {book.get('isbn', '-')}\n"
            f"   作者: {book.get('author', '-')}\n"
            f"   出版社: {book.get('publisher', '-')}\n"
            f"   类别: {book.get('category', '-')}\n"
            f"   价格: ¥{book.get('price', 0)}\n"
            f"   库存: {book.get('stock', 0)} 本\n"
            f"   评分: {book.get('rating', 0)} / 5\n"
            f"   标签: {tags}\n"
            f"   累计借阅: {book.get('borrow_count', 0)} 次"
        )

    def _format_books_list(self, books):
        """图书列表格式化。"""
        lines = []
        for i, b in enumerate(books, 1):
            lines.append(
                f"{i}. 《{b.get('title', '未知')}》 "
                f"| {b.get('author', '-')} "
                f"| ¥{b.get('price', 0)} "
                f"| 库存:{b.get('stock', 0)} "
                f"| 评分:{b.get('rating', 0)}"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    # 简单测试
    bm = BookManager()
    print(bm.top_rated(5))
    print("---")
    print(bm.find_by_isbn("9787115428028"))
