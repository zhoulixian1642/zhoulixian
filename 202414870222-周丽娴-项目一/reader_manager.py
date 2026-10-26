# -*- coding: utf-8 -*-
"""
reader_manager.py
读者管理模块：读者信息管理、学院统计、等级分布。
"""

from mongodb_connect import get_db


class ReaderManager:
    def __init__(self):
        self.db = get_db()
        self.col = self.db.readers

    # ---------- 查询 ----------
    def find_by_card(self, card_no):
        """按借阅证号查找读者。"""
        reader = self.col.find_one({"card_no": card_no})
        if not reader:
            return f"⚠️ 未找到证号为 {card_no} 的读者"
        return self._format_reader(reader)

    def list_all(self):
        """列出所有读者。"""
        cursor = self.col.find()
        readers = list(cursor)
        if not readers:
            return "⚠️ 暂无读者数据"
        lines = []
        for i, r in enumerate(readers, 1):
            lines.append(
                f"{i}. {r.get('name', '-')} "
                f"| 证号:{r.get('card_no', '-')} "
                f"| {r.get('college', '-')} "
                f"| {r.get('level', '-')}"
            )
        return "\n".join(lines)

    def find_by_college(self, college):
        """按学院筛选读者。"""
        cursor = self.col.find({"college": {"$regex": college}})
        readers = list(cursor)
        if not readers:
            return f"⚠️ {college} 相关学院暂无读者"
        lines = [f"📚 {college} 相关学院读者："]
        for i, r in enumerate(readers, 1):
            lines.append(f"  {i}. {r['name']} | {r['card_no']} | {r['level']}")
        return "\n".join(lines)

    # ---------- 统计 ----------
    def count_by_college(self):
        """按学院统计读者人数。"""
        pipeline = [
            {"$group": {"_id": "$college", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = list(self.col.aggregate(pipeline))
        lines = ["🏫 各学院读者人数："]
        for item in result:
            lines.append(f"  {item['_id']}: {item['count']} 人")
        return "\n".join(lines)

    def count_by_level(self):
        """按借阅等级统计人数分布。"""
        pipeline = [
            {"$group": {"_id": "$level", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = list(self.col.aggregate(pipeline))
        lines = ["🏷️ 借阅等级分布："]
        for item in result:
            lines.append(f"  {item['_id']}: {item['count']} 人")
        return "\n".join(lines)

    def distinct_colleges(self):
        """获取所有学院清单。"""
        colleges = self.col.distinct("college")
        return "🏫 所有学院：\n  " + "\n  ".join(colleges)

    def count_total(self):
        """读者总数。"""
        n = self.col.count_documents({})
        return f"👥 读者总数: {n} 人"

    # ---------- 添加 / 更新 / 删除 ----------
    def add_reader(self, reader_dict):
        """添加新读者。"""
        result = self.col.insert_one(reader_dict)
        return f"✅ 读者添加成功，_id: {result.inserted_id}"

    def update_reader(self, card_no, **kwargs):
        """更新读者信息。"""
        result = self.col.update_one({"card_no": card_no}, {"$set": kwargs})
        if result.matched_count == 0:
            return "⚠️ 未找到该读者"
        return f"✅ 读者信息已更新，受影响文档数: {result.modified_count}"

    def replace_reader(self, card_no, new_info):
        """整体替换读者信息（保留 _id）。"""
        result = self.col.replace_one({"card_no": card_no}, new_info)
        if result.matched_count == 0:
            return "⚠️ 未找到该读者"
        return f"✅ 读者信息已整体替换，修改文档数: {result.modified_count}"

    def delete_reader(self, card_no):
        """删除读者。"""
        result = self.col.delete_one({"card_no": card_no})
        if result.deleted_count == 0:
            return "⚠️ 未找到该读者"
        return f"✅ 读者已删除，删除文档数: {result.deleted_count}"

    # ---------- 格式化 ----------
    def _format_reader(self, r):
        fav = "、".join(r.get("fav_categories", [])) or "无偏好"
        email = r.get("email") or "未填写"
        return (
            f"👤 {r.get('name', '未知')}\n"
            f"   证号: {r.get('card_no', '-')}\n"
            f"   学院: {r.get('college', '-')}\n"
            f"   邮箱: {email}\n"
            f"   电话: {r.get('phone', '-')}\n"
            f"   等级: {r.get('level', '-')}\n"
            f"   偏好类别: {fav}"
        )


if __name__ == "__main__":
    rm = ReaderManager()
    print(rm.count_total())
    print("---")
    print(rm.count_by_college())
    print("---")
    print(rm.find_by_card("R20240001"))
