# -*- coding: utf-8 -*-
"""
main.py
图书情报检索与统计平台 - 主程序
菜单式命令行交互，串联各功能模块。
"""

from mongodb_connect import check_connection, get_client
from book_manager import BookManager
from reader_manager import ReaderManager
from borrow_manager import BorrowManager
from stat_manager import StatManager


def print_menu():
    """打印主菜单。"""
    print("\n" + "=" * 50)
    print("      📚 图书情报检索与统计平台")
    print("=" * 50)
    print("  1. 图书查询检索")
    print("  2. 图书管理（增删改）")
    print("  3. 读者信息管理")
    print("  4. 借阅与归还操作")
    print("  5. 统计分析报表")
    print("  6. 热门排行（图书/读者）")
    print("  7. 数据更新操作")
    print("  8. 数据删除操作")
    print("  0. 退出系统")
    print("=" * 50)


def print_book_menu():
    print("\n--- 图书查询 ---")
    print("  1. 按 ISBN 精确查找")
    print("  2. 按书名关键词模糊搜索")
    print("  3. 多条件筛选（价格/类别/评分）")
    print("  0. 返回主菜单")


def print_stat_menu():
    print("\n--- 统计分析 ---")
    print("  1. 按类别统计图书")
    print("  2. 出版社 Top5")
    print("  3. 各年度借阅趋势")
    print("  4. 学院借阅量排行")
    print("  5. 图书销售额统计")
    print("  0. 返回主菜单")


def main():
    # 启动时检查连接
    print("正在连接数据库...")
    ok, stats = check_connection()
    if not ok:
        print("❌ 数据库连接失败！请确认 MongoDB 已启动（端口 27017）。")
        return

    print("✅ 数据库连接成功！")
    print(f"   图书: {stats.get('books', 0)} 本")
    print(f"   读者: {stats.get('readers', 0)} 人")
    print(f"   借阅记录: {stats.get('borrow_logs', 0)} 条")

    # 初始化各模块
    bm = BookManager()
    rm = ReaderManager()
    brm = BorrowManager()
    sm = StatManager()

    client = get_client()

    while True:
        print_menu()
        choice = input("请输入选项: ").strip()

        if choice == "0":
            print("👋 感谢使用，再见！")
            break

        elif choice == "1":
            # 图书查询
            while True:
                print_book_menu()
                sub = input("请选择: ").strip()
                if sub == "0":
                    break
                elif sub == "1":
                    isbn = input("输入 ISBN: ").strip()
                    print(bm.find_by_isbn(isbn))
                elif sub == "2":
                    kw = input("输入书名关键词: ").strip()
                    print(bm.search_by_title(kw))
                elif sub == "3":
                    cat = input("类别（回车跳过）: ").strip() or None
                    min_r = input("最低评分（回车跳过）: ").strip()
                    min_r = float(min_r) if min_r else None
                    print(bm.filter_books(category=cat, min_rating=min_r))
                else:
                    print("无效选项")

        elif choice == "2":
            # 图书管理（增删改）
            print("\n--- 图书管理 ---")
            print("  1. 添加新图书")
            print("  2. 修改图书信息")
            sub = input("请选择: ").strip()
            if sub == "1":
                title = input("书名: ").strip()
                isbn = input("ISBN: ").strip()
                author = input("作者: ").strip()
                price = float(input("价格: ").strip())
                stock = int(input("库存: ").strip())
                book = {
                    "title": title, "isbn": isbn, "author": author,
                    "price": price, "stock": stock, "rating": 0.0,
                    "category": "未分类", "borrow_count": 0
                }
                print(bm.add_book(book))
            elif sub == "2":
                isbn = input("要修改的 ISBN: ").strip()
                field = input("修改字段（price/stock/rating）: ").strip()
                val = input("新值: ").strip()
                if field in ("price", "rating"):
                    val = float(val)
                else:
                    val = int(val)
                print(bm.update_book_info(isbn, **{field: val}))

        elif choice == "3":
            # 读者管理
            print("\n--- 读者管理 ---")
            print("  1. 按证号查读者")
            print("  2. 列出所有读者")
            print("  3. 各学院人数统计")
            print("  4. 借阅等级分布")
            sub = input("请选择: ").strip()
            if sub == "1":
                card = input("借阅证号: ").strip()
                print(rm.find_by_card(card))
            elif sub == "2":
                print(rm.list_all())
            elif sub == "3":
                print(rm.count_by_college())
            elif sub == "4":
                print(rm.count_by_level())

        elif choice == "4":
            # 借阅操作
            print("\n--- 借阅管理 ---")
            print("  1. 登记借阅")
            print("  2. 归还图书")
            print("  3. 查当前在借")
            print("  4. 查逾期记录")
            sub = input("请选择: ").strip()
            if sub == "1":
                card = input("读者证号: ").strip()
                isbn = input("图书 ISBN: ").strip()
                print(brm.borrow_book(card, isbn))
            elif sub == "2":
                card = input("读者证号: ").strip()
                isbn = input("图书 ISBN: ").strip()
                print(brm.return_book(card, isbn))
            elif sub == "3":
                print(brm.list_current_borrowed())
            elif sub == "4":
                print(brm.list_overdue())

        elif choice == "5":
            # 统计分析
            while True:
                print_stat_menu()
                sub = input("请选择: ").strip()
                if sub == "0":
                    break
                elif sub == "1":
                    print(sm.category_stats())
                elif sub == "2":
                    print(sm.publisher_top())
                elif sub == "3":
                    print(sm.borrow_trend_by_year())
                elif sub == "4":
                    print(sm.college_borrow_ranking())
                elif sub == "5":
                    print(sm.book_sales())

        elif choice == "6":
            # 热门排行
            print("\n--- 热门排行 ---")
            print("  1. 评分最高 Top5")
            print("  2. 借阅最多 Top5（畅销榜）")
            print("  3. 活跃读者 Top5")
            sub = input("请选择: ").strip()
            if sub == "1":
                print(bm.top_rated(5))
            elif sub == "2":
                print(bm.top_borrowed(5))
            elif sub == "3":
                print(sm.top_readers(5))

        elif choice == "7":
            # 数据更新
            print("\n--- 数据更新 ---")
            print("  1. 某图书库存增减")
            print("  2. 某类别图书统一打折")
            sub = input("请选择: ").strip()
            if sub == "1":
                isbn = input("ISBN: ").strip()
                delta = int(input("增减数量（负数表示减少）: ").strip())
                print(bm.update_stock(isbn, delta))
            elif sub == "2":
                cat = input("类别: ").strip()
                ratio = float(input("折扣（如0.9表示9折）: ").strip())
                print(bm.update_price_by_category(cat, ratio))

        elif choice == "8":
            # 数据删除
            print("\n--- 数据删除 ---")
            print("  1. 删除一本图书")
            print("  2. 清理逾期借阅记录")
            sub = input("请选择: ").strip()
            if sub == "1":
                isbn = input("要删除的 ISBN: ").strip()
                confirm = input(f"确认删除 {isbn}？(y/n): ").strip()
                if confirm.lower() == "y":
                    print(bm.delete_book(isbn))
                else:
                    print("已取消")
            elif sub == "2":
                print(brm.list_overdue())
                confirm = input("确认清理以上所有逾期记录？(y/n): ").strip()
                if confirm.lower() == "y":
                    print(brm.delete_overdue_logs())
                else:
                    print("已取消")

        else:
            print("无效选项，请重新输入")

    # 退出前关闭连接
    close_client(client)


if __name__ == "__main__":
    main()
