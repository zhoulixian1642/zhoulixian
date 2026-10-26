# -*- coding: utf-8 -*-
"""
生成技术文档 Word 版本
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 设置默认字体
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)

# 标题
title = doc.add_heading('图书情报检索与统计平台 技术文档', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ========== 一、项目概述 ==========
doc.add_heading('一、项目概述', level=1)

doc.add_paragraph('1. 项目背景')
p = doc.add_paragraph(
    '某高校图书馆拟建设图书情报检索与统计平台，用于管理馆藏图书与读者借阅记录，'
    '并提供多维度检索与统计服务。本项目基于 MongoDB 数据库完成从环境部署、数据建模、'
    '检索功能、统计报表到应用程序开发的完整流程。'
)

doc.add_paragraph('2. 业务目标')
doc.add_paragraph('• 实现图书、读者、借阅流水三类数据的存储与管理', style='List Bullet')
doc.add_paragraph('• 提供精确查询、范围查询、组合条件查询等多种检索方式', style='List Bullet')
doc.add_paragraph('• 支持分类统计、借阅趋势、热门排行等聚合分析', style='List Bullet')
doc.add_paragraph('• 开发菜单式命令行应用，方便日常使用', style='List Bullet')

doc.add_paragraph('3. 组内分工（三人小组）')
doc.add_paragraph('• 同学A：负责任务一、二 —— 环境部署与数据建模', style='List Bullet')
doc.add_paragraph('• 同学B：负责任务三、四 —— 检索功能与统计权限', style='List Bullet')
doc.add_paragraph('• 同学C：负责任务五、六 —— 程序开发与验收交付', style='List Bullet')


# ========== 二、环境与数据建模 ==========
doc.add_heading('二、环境与数据建模', level=1)

doc.add_paragraph('1. 部署关键参数')
doc.add_paragraph('• MongoDB 版本：社区版 6.0+', style='List Bullet')
doc.add_paragraph('• 服务端口：27017（默认）', style='List Bullet')
doc.add_paragraph('• 数据目录：自定义创建（如 D:\\mongodb\\data）', style='List Bullet')
doc.add_paragraph('• Python 版本：3.9+，驱动：pymongo', style='List Bullet')

doc.add_paragraph('2. 四个业务集合设计')

# 表格
table = doc.add_table(rows=5, cols=3)
table.style = 'Light Grid Accent 1'
hdr = table.rows[0].cells
hdr[0].text = '集合名'
hdr[1].text = '用途'
hdr[2].text = '核心字段'

row1 = table.rows[1].cells
row1[0].text = 'books'
row1[1].text = '图书信息'
row1[2].text = 'isbn, title, author, category, price, stock, rating, tags'

row2 = table.rows[2].cells
row2[0].text = 'readers'
row2[1].text = '读者信息'
row2[2].text = 'card_no, name, college, level, email, phone'

row3 = table.rows[3].cells
row3[0].text = 'borrow_logs'
row3[1].text = '借阅流水'
row3[2].text = 'borrow_date, return_date, reader_card, book_isbn, status'

row4 = table.rows[4].cells
row4[0].text = 'category_stats'
row4[1].text = '统计结果'
row4[2].text = '_id(类别), book_count, avg_rating'

doc.add_paragraph('')
doc.add_paragraph('3. 三种特殊集合实现方式')
doc.add_paragraph('• 固定集合 book_logs：capped 模式，大小 1MB，最多 1000 条，自动淘汰旧数据', style='List Bullet')
doc.add_paragraph('• 时间序列集合 borrow_logs：timeField 设为 borrow_date，granularity 设为 hours，2 年自动过期', style='List Bullet')
doc.add_paragraph('• 视图 book_in_stock：基于 books 集合，管道过滤 stock > 0 的图书', style='List Bullet')

doc.add_paragraph('4. 索引设计')
doc.add_paragraph('• 唯一索引：books.isbn（防止重复 ISBN）', style='List Bullet')
doc.add_paragraph('• 单键索引：books.title、books.category', style='List Bullet')
doc.add_paragraph('• 多键索引：books.tags', style='List Bullet')
doc.add_paragraph('• 复合索引：(category, price) 加速分类+价格联合查询', style='List Bullet')


# ========== 三、功能实现 ==========
doc.add_heading('三、功能实现', level=1)

doc.add_paragraph('1. 检索功能（任务三）')
doc.add_paragraph(
    '实现了 16 条查询操作，覆盖基础检索（$gt、$lt、$eq、$ne、$in）、'
    '组合检索（$and、$or、$regex、$all、$size、$exists）以及结果处理（$type、sort+limit、投影、distinct）。'
    '同时实现了 7 条更新删除操作，包括 $inc 增减库存、$mul 批量打折、$currentDate 记录时间、'
    '$unset 删除字段，以及 deleteOne/deleteMany/replaceOne。'
)

doc.add_paragraph('2. 统计分析（任务四）')
doc.add_paragraph(
    '使用聚合管道完成 9 项统计：按类别分组统计数量与平均评分、'
    '出版社 Top5、sortByCount 找最多类别、评分最高 3 本、'
    '销售额计算（$multiply + $round）、按年份格式化借阅趋势、'
    '读者借阅次数排行、$lookup 关联学院借阅量、$merge 写入统计集合。'
)

doc.add_paragraph('3. 权限管理')
doc.add_paragraph(
    '创建了两个账号：libReader（只读角色）和 libWriter（readWrite + dbAdmin 角色）。'
    '启用访问控制后，只读账号无法执行写操作，验证了权限隔离效果。'
)

doc.add_paragraph('4. Python 应用程序（任务五）')
doc.add_paragraph(
    '采用模块化设计，共 6 个文件：'
    'mongodb_connect.py（连接封装）、book_manager.py（图书管理）、'
    'reader_manager.py（读者管理）、borrow_manager.py（借阅管理）、'
    'stat_manager.py（统计分析）、main.py（菜单主程序）。'
    '主程序启动时显示连接状态和各集合文档数，菜单包含 8 个功能项，'
    '覆盖检索、统计、更新、删除，操作后打印受影响文档数。'
)


# ========== 四、问题与核对 ==========
doc.add_heading('四、问题与核对', level=1)

doc.add_paragraph('1. 调试难点与排查')

doc.add_paragraph('难点一：时间序列集合创建失败')
doc.add_paragraph(
    '问题：第一次创建 borrow_logs 时间序列集合时报错。'
    '原因：集合名已经存在（之前先建了普通集合）。'
    '解决：先 db.borrow_logs.drop() 删除旧集合，再按时间序列参数重新创建。'
)

doc.add_paragraph('难点二：$lookup 关联查不到数据')
doc.add_paragraph(
    '问题：关联 readers 和 borrow_logs 时结果为空。'
    '原因：reader_card 字段类型不一致（一个是字符串一个是其他类型）。'
    '解决：确认两边都是字符串类型后，$lookup 正常返回结果。'
)

doc.add_paragraph('2. 命令行与 Compass 结果核对')
doc.add_paragraph('用 Compass 连接同一实例，逐项核对：')
doc.add_paragraph('• Q1 定价 80 元以上：命令行 7 条，Compass 一致 ✓', style='List Bullet')
doc.add_paragraph('• Q2 库存不足 10 本：命令行 8 条，Compass 一致 ✓', style='List Bullet')
doc.add_paragraph('• Q14 评分前 5：命令行结果与 Compass 排序一致 ✓', style='List Bullet')
doc.add_paragraph('• A1 分类统计：各分类数量与聚合结果一致 ✓', style='List Bullet')
doc.add_paragraph('• 视图 book_in_stock：数量等于 stock>0 的图书数 ✓', style='List Bullet')

# 保存
output_path = r'C:\Users\周丽娴\Doubao\chats\2026-10-26\new-chat\library_platform\docs\技术文档.docx'
doc.save(output_path)
print(f"技术文档已生成: {output_path}")
