# -*- coding: utf-8 -*-
"""
mongodb_connect.py
数据库连接模块：封装 MongoDB 连接逻辑，供其他模块统一调用。
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# ========== 连接参数（统一在这里改） ==========
HOST = "localhost"
PORT = 27017
DB_NAME = "library"
USERNAME = ""        # 若启用了访问控制，填用户名；未启用留空
PASSWORD = ""       # 对应密码
AUTH_SOURCE = "admin"  # 认证数据库，默认 admin
# ==============================================


def get_client():
    """获取 MongoDB 客户端连接。"""
    if USERNAME and PASSWORD:
        uri = f"mongodb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/?authSource={AUTH_SOURCE}"
        return MongoClient(uri)
    return MongoClient(HOST, PORT)


def get_db():
    """获取 library 数据库对象。"""
    client = get_client()
    return client[DB_NAME]


def check_connection():
    """检查连接是否正常，返回 (是否成功, 各集合文档数字典)。"""
    try:
        client = get_client()
        # 用 admin 命令 ping 一下确认连接
        client.admin.command("ping")
        db = client[DB_NAME]
        stats = {
            "books": db.books.count_documents({}),
            "readers": db.readers.count_documents({}),
            "borrow_logs": db.borrow_logs.count_documents({}),
            "category_stats": db.category_stats.count_documents({}),
        }
        return True, stats
    except ConnectionFailure:
        return False, {}
    except Exception as e:
        return False, {"error": str(e)}


def close_client(client):
    """关闭客户端连接。"""
    if client:
        client.close()


if __name__ == "__main__":
    # 单独运行本文件时做连接测试
    ok, info = check_connection()
    if ok:
        print("✅ 数据库连接成功！")
        print(f"   数据库: {DB_NAME}")
        for k, v in info.items():
            print(f"   {k}: {v} 条文档")
    else:
        print("❌ 数据库连接失败，请检查 MongoDB 是否已启动。")
        if info:
            print(f"   错误信息: {info}")
