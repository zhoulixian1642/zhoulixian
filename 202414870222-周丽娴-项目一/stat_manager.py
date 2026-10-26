# -*- coding: utf-8 -*-
"""
stat_manager.py
统计分析模块：分类统计、借阅趋势、畅销榜。
全部使用聚合管道（aggregate）实现。
"""

from mongodb_connect import get_db


class StatManager:
    def __init__(self):
        self.db = get_db()
        self.books = self.db.books
        self.logs = self.db.borrow_logs
        self.readers = self.db.readers

    # ---------- A1: 按类别统计图书数量与平均评分 ----------
    def category_stats(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "book_count": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"},
                    "total_stock": {"$sum": "$stock"},
                    "avg_price": {"$avg": "$price"}
                }
            },
            {"$sort": {"book_count": -1}}
        ]
        result = list(self.books.aggregate(pipeline))
        lines = ["📊 按类别统计："]
        for item in result:
            lines.append(
                f"  {item['_id']}: "
                f"{item['book_count']}本, "
                f"平均评分{item['avg_rating']:.2f}, "
                f"库存合计{item['total_stock']}, "
                f"均价¥{item['avg_price']:.1f}"
            )
        # 同时把结果写入 category_stats 集合
        if result:
            self.db.category_stats.drop()
            self.db.category_stats.insert_many(result)
            lines.append(f"\n💾 统计结果已写入 category_stats 集合（共 {len(result)} 条）")
        return "\n".join(lines)

    # ---------- A2: 各出版社图书数量 Top5 ----------
    def publisher_top(self, n=5):
        pipeline = [
            {"$group": {"_id": "$publisher", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": n}
        ]
        result = list(self.books.aggregate(pipeline))
        lines = [f"🏢 图书数量最多的前 {n} 家出版社："]
        for i, item in enumerate(result, 1):
            lines.append(f"  {i}. {item['_id']}: {item['count']} 本")
        return "\n".join(lines)

    # ---------- A4: 评分最高的 3 本图书 ----------
    def top_rated_books(self, n=3):
        pipeline = [
            {"$sort": {"rating": -1}},
            {"$limit": n},
            {"$project": {"title": 1, "rating": 1, "borrow_count": 1, "_id": 0}}
        ]
        result = list(self.books.aggregate(pipeline))
        lines = [f"⭐ 评分最高的前 {n} 本："]
        for i, item in enumerate(result, 1):
            lines.append(
                f"  {i}. 《{item['title']}》 "
                f"| 评分:{item['rating']} "
                f"| 借阅:{item['borrow_count']}次"
            )
        return "\n".join(lines)

    # ---------- A5: 每本书销售额（单价×借阅次数） ----------
    def book_sales(self):
        pipeline = [
            {
                "$project": {
                    "title": 1,
                    "price": 1,
                    "borrow_count": 1,
                    "sales": {
                        "$round": [{"$multiply": ["$price", "$borrow_count"]}, 2]
                    },
                    "_id": 0
                }
            },
            {"$sort": {"sales": -1}}
        ]
        result = list(self.books.aggregate(pipeline))
        lines = ["💰 每本书销售额（单价×借阅次数）："]
        for i, item in enumerate(result, 1):
            lines.append(
                f"  {i}. 《{item['title']}》 "
                f"| ¥{item['price']} × {item['borrow_count']}次 "
                f"= ¥{item['sales']}"
            )
        return "\n".join(lines)

    # ---------- A6: 按借阅年份统计借阅量 ----------
    def borrow_trend_by_year(self):
        pipeline = [
            {
                "$group": {
                    "_id": {"$year": "$borrow_date"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        result = list(self.logs.aggregate(pipeline))
        lines = ["📈 各年度借阅量："]
        for item in result:
            lines.append(f"  {item['_id']}年: {item['count']} 次")
        return "\n".join(lines)

    # ---------- A7: 每位读者借阅次数 Top5 ----------
    def top_readers(self, n=5):
        pipeline = [
            {"$group": {"_id": "$reader_card", "borrow_times": {"$sum": 1}}},
            {"$sort": {"borrow_times": -1}},
            {"$limit": n}
        ]
        result = list(self.logs.aggregate(pipeline))
        lines = [f"🏆 借阅次数最多的前 {n} 名读者："]
        for i, item in enumerate(result, 1):
            # 关联查姓名
            r = self.readers.find_one({"card_no": item["_id"]})
            name = r["name"] if r else item["_id"]
            lines.append(f"  {i}. {name}({item['_id']}): {item['borrow_times']} 次")
        return "\n".join(lines)

    # ---------- A8: 学院借阅量排行榜 ----------
    def college_borrow_ranking(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "readers",
                    "localField": "reader_card",
                    "foreignField": "card_no",
                    "as": "reader_info"
                }
            },
            {"$unwind": "$reader_info"},
            {
                "$group": {
                    "_id": "$reader_info.college",
                    "borrow_count": {"$sum": 1}
                }
            },
            {"$sort": {"borrow_count": -1}}
        ]
        result = list(self.logs.aggregate(pipeline))
        lines = ["🎓 各学院借阅量排行："]
        for i, item in enumerate(result, 1):
            lines.append(f"  {i}. {item['_id']}: {item['borrow_count']} 次")
        return "\n".join(lines)

    # ---------- 畅销榜（按图书借阅次数） ----------
    def best_seller_books(self, n=10):
        pipeline = [
            {"$sort": {"borrow_count": -1}},
            {"$limit": n},
            {"$project": {"title": 1, "author": 1, "borrow_count": 1, "category": 1, "_id": 0}}
        ]
        result = list(self.books.aggregate(pipeline))
        lines = [f"🔥 畅销榜 Top {n}："]
        for i, item in enumerate(result, 1):
            lines.append(
                f"  {i}. 《{item['title']}》 "
                f"| {item['author']} "
                f"| {item['category']} "
                f"| 借阅 {item['borrow_count']} 次"
            )
        return "\n".join(lines)


if __name__ == "__main__":
    sm = StatManager()
    print(sm.category_stats())
    print("---")
    print(sm.borrow_trend_by_year())
    print("---")
    print(sm.top_readers())
