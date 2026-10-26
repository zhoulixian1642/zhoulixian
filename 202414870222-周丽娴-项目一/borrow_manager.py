# -*- coding: utf-8 -*-
"""
borrow_manager.py
借阅管理模块：借阅登记、归还处理、逾期查询。
"""

from datetime import datetime
from mongodb_connect import get_db


class BorrowManager:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.borrow_logs
        self.books_col = self.db.books

    # ---------- 借阅登记 ----------
    def borrow_book(self, reader_card, book_isbn):
        """
        登记一条借阅记录。
        同时扣减图书库存、增加累计借阅次数。
        """
        # 检查图书是否存在且有库存
        book = self.books_col.find_one({"isbn": book_isbn})
        if not book:
            return "⚠️ 该 ISBN 的图书不存在"
        if book.get("stock", 0) <= 0:
            return "⚠️ 该书库存为 0，无法借阅"

        # 写入借阅记录
        log = {
            "borrow_date": datetime.now(),
            "reader_card": reader_card,
            "book_isbn": book_isbn,
            "status": "借出"
        }
        result = self.col.insert_one(log)

        # 扣库存 + 加借阅次数
        self.books_col.update_one(
            {"isbn": book_isbn},
            {"$inc": {"stock": -1, "borrow_count": 1}}
        )

        return (f"✅ 借阅登记成功！\n"
                f"   记录ID: {result.inserted_id}\n"
                f"   读者: {reader_card}\n"
                f"   图书: {book_isbn}\n"
                f"   借阅时间: {log['borrow_date'].strftime('%Y-%m-%d %H:%M')}")

    # ---------- 归还处理 ----------
    def return_book(self, reader_card, book_isbn):
        """归还图书：找到当前借出的记录，更新状态和归还时间。"""
        result = self.col.update_one(
            {"reader_card": reader_card, "book_isbn": book_isbn, "status": "借出"},
            {"$set": {"status": "已归还", "return_date": datetime.now()}}
        )
        if result.matched_count == 0:
            return "⚠️ 未找到该读者的在借记录"

        # 库存加回
        self.books_col.update_one(
            {"isbn": book_isbn},
            {"$inc": {"stock": 1}}
        )
        return f"✅ 归还成功，更新记录数: {result.modified_count}"

    def batch_return(self, status_list=None):
        """批量处理（示例：把超过某时间的借出标记为逾期）。"""
        if status_list is None:
            status_list = ["借出"]
        result = self.col.update_many(
            {"status": {"$in": status_list}},
            {"$set": {"status": "已归还"}}
        )
        return f"✅ 批量更新完成，共修改 {result.modified_count} 条记录"

    # ---------- 查询 ----------
    def list_borrowed_by_reader(self, reader_card):
        """查某读者的所有借阅记录。"""
        cursor = self.col.find({"reader_card": reader_card}).sort("borrow_date", -1)
        logs = list(cursor)
        if not logs:
            return f"⚠️ 读者 {reader_card} 暂无借阅记录"
        lines = [f"📋 读者 {reader_card} 的借阅记录："]
        for i, log in enumerate(logs, 1):
            bdate = log.get("borrow_date")
            bdate_str = bdate.strftime("%Y-%m-%d") if bdate else "-"
            lines.append(
                f"  {i}. {log.get('book_isbn', '-')} "
                f"| 借出:{bdate_str} "
                f"| 状态:{log.get('status', '-')}"
            )
        return "\n".join(lines)

    def list_overdue(self):
        """查所有逾期记录。"""
        cursor = self.col.find({"status": "逾期"})
        logs = list(cursor)
        if not logs:
            return "✅ 当前没有逾期记录"
        lines = [f"⏰ 共 {len(logs)} 条逾期记录："]
        for i, log in enumerate(logs, 1):
            bdate = log.get("borrow_date")
            bdate_str = bdate.strftime("%Y-%m-%d") if bdate else "-"
            lines.append(
                f"  {i}. 读者:{log.get('reader_card')} "
                f"| 图书:{log.get('book_isbn')} "
                f"| 借出:{bdate_str}"
            )
        return "\n".join(lines)

    def list_current_borrowed(self):
        """查当前所有在借（未归还）的记录。"""
        cursor = self.col.find({"status": "借出"})
        logs = list(cursor)
        if not logs:
            return "✅ 当前没有在借图书"
        lines = [f"📚 当前在借 {len(logs)} 条："]
        for i, log in enumerate(logs, 1):
            bdate = log.get("borrow_date")
            bdate_str = bdate.strftime("%Y-%m-%d") if bdate else "-"
            lines.append(
                f"  {i}. 读者:{log.get('reader_card')} "
                f"| 图书:{log.get('book_isbn')} "
                f"| 借出:{bdate_str}"
            )
        return "\n".join(lines)

    # ---------- 删除 ----------
    def delete_one_log(self, log_id):
        """删除一条借阅记录。"""
        from bson.objectid import ObjectId
        result = self.col.delete_one({"_id": ObjectId(log_id)})
        if result.deleted_count == 0:
            return "⚠️ 未找到该记录"
        return f"✅ 记录已删除，删除条数: {result.deleted_count}"

    def delete_overdue_logs(self):
        """清理所有逾期记录（先预览数量再删）。"""
        n = self.col.count_documents({"status": "逾期"})
        result = self.col.delete_many({"status": "逾期"})
        return (f"🗑️ 逾期记录清理完成\n"
                f"   清理前预览: {n} 条\n"
                f"   实际删除: {result.deleted_count} 条")

    def count_total(self):
        """借阅记录总数。"""
        n = self.col.count_documents({})
        return f"📝 借阅记录总数: {n} 条"


if __name__ == "__main__":
    bm = BorrowManager()
    print(bm.count_total())
    print("---")
    print(bm.list_overdue())
    print("---")
    print(bm.list_current_borrowed())
