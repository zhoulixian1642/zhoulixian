# 图书情报检索与统计平台 - 运行说明

## 一、环境准备

### 1. 安装 MongoDB
- 下载并安装 MongoDB 社区版（6.0 或以上）
- 安装后确保 `mongod` 命令可用（配置环境变量）
- 创建数据目录，如 `D:\mongodb\data`

### 2. 启动 MongoDB
```bash
mongod --dbpath D:\mongodb\data
```
看到 `Waiting for connections` 即启动成功，默认端口 27017。

### 3. 安装 Python 依赖
```bash
pip install pymongo
```

---

## 二、导入数据

### 方法一：用 mongoimport 命令导入（推荐）

打开新的终端窗口，进入 `data` 目录，执行：

```bash
mongoimport --db library --collection books --file books.json --jsonArray
mongoimport --db library --collection readers --file readers.json --jsonArray
mongoimport --db library --collection borrow_logs --file borrow_logs.json --jsonArray
```

> 注意：borrow_logs 是时间序列集合，需要先手动创建再导入。如果直接导入会自动创建普通集合。
> 建议先在 mongosh 里执行 `scripts/run_all_commands.js` 里的创建集合语句，再导入数据。

### 方法二：用 mongosh 手动创建

打开 mongosh，依次执行：
```js
use library;
db.createCollection("books");
db.createCollection("readers");
db.createCollection("category_stats");

// 固定集合
db.createCollection("book_logs", { capped: true, size: 1048576, max: 1000 });

// 时间序列集合
db.createCollection("borrow_logs", {
  timeseries: { timeField: "borrow_date", granularity: "hours" },
  expireAfterSeconds: 63072000
});

// 视图
db.createView("book_in_stock", "books", [{ $match: { stock: { $gt: 0 } } }]);
```

然后再用上面的 mongoimport 命令导入数据。

---

## 三、运行 Python 程序

### 1. 测试数据库连接
```bash
python mongodb_connect.py
```
显示"数据库连接成功"和各集合文档数即正常。

### 2. 启动主程序
```bash
python main.py
```

启动后会显示菜单：
```
==================================================
      📚 图书情报检索与统计平台
==================================================
  1. 图书查询检索
  2. 图书管理（增删改）
  3. 读者信息管理
  4. 借阅与归还操作
  5. 统计分析报表
  6. 热门排行（图书/读者）
  7. 数据更新操作
  8. 数据删除操作
  0. 退出系统
==================================================
请输入选项:
```

输入数字选择功能，按提示操作即可。

---

## 四、文件说明

```
library_platform/
├── data/                    # 数据文件
│   ├── books.json           # 图书数据（20条）
│   ├── readers.json         # 读者数据（16条）
│   └── borrow_logs.json     # 借阅记录（65条）
│
├── scripts/                 # 脚本
│   ├── run_all_commands.js  # mongosh 全部命令（任务二三四）
│   └── gen_doc.py           # 生成技术文档脚本
│
├── docs/                    # 文档
│   ├── 技术文档.md           # 技术文档（可复制到Word）
│   └── 技术文档.docx         # Word版（需python-docx）
│
├── mongodb_connect.py       # 数据库连接模块
├── book_manager.py          # 图书管理模块
├── reader_manager.py        # 读者管理模块
├── borrow_manager.py        # 借阅管理模块
├── stat_manager.py          # 统计分析模块
├── main.py                  # 主程序（菜单入口）
└── README.md                # 本说明
```

---

## 五、常见问题

**Q: 启动 main.py 报 "连接失败"？**
A: 先确认 MongoDB 已经启动（mongod 命令在运行），端口是 27017。

**Q: 导入数据时报集合不存在？**
A: 时间序列集合和固定集合需要先手动创建，不能直接 mongoimport。

**Q: 统计结果为空？**
A: 确认数据已经导入成功，在 mongosh 里执行 `db.books.countDocuments()` 看数量。

**Q: 想改连接配置？**
A: 编辑 `mongodb_connect.py` 顶部的 HOST、PORT、DB_NAME。
