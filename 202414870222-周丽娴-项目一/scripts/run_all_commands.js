// ============================================================
// 图书情报检索与统计平台 - mongosh 命令脚本
// 覆盖：任务二（数据建模）、任务三（检索功能）、任务四（统计与权限）
// 使用方法：mongosh < run_all_commands.js
// ============================================================

// ========== 任务二：数据建模与填充 ==========

// 2.1 创建数据库和普通集合
use library;

db.createCollection("books");
db.createCollection("readers");
db.createCollection("category_stats");

// 2.2 创建特殊集合

// 固定集合 book_logs：1MB 上限，最多 1000 条
db.createCollection("book_logs", {
  capped: true,
  size: 1048576,    // 1MB
  max: 1000
});

// 时间序列集合 borrow_logs：时间字段 borrow_date，小时粒度，2 年过期
db.createCollection("borrow_logs", {
  timeseries: {
    timeField: "borrow_date",
    granularity: "hours"
  },
  expireAfterSeconds: 63072000   // 2 年
});

// 视图 book_in_stock：库存大于 0 的图书
db.createView("book_in_stock", "books", [
  { $match: { stock: { $gt: 0 } } }
]);

// 查看所有集合（验证特殊集合类型标记）
show collections;

// 查看固定集合配置
db.getCollectionInfos({name: "book_logs"});

// 查看时间序列集合配置
db.getCollectionInfos({name: "borrow_logs"});

// 2.3 导入数据（命令行用 mongoimport，这里用 insertMany 示例）
// 实际导入命令（在终端执行）：
// mongoimport --db library --collection books --file books.json --jsonArray
// mongoimport --db library --collection readers --file readers.json --jsonArray
// mongoimport --db library --collection borrow_logs --file borrow_logs.json --jsonArray

// 用 insertOne 单独录一条
db.books.insertOne({
  isbn: "9787111000001",
  title: "测试图书",
  author: "测试作者",
  publisher: "测试出版社",
  category: "计算机",
  price: 50.0,
  stock: 10,
  rating: 4.0,
  tags: ["测试"],
  publish_date: new Date("2024-01-01"),
  borrow_count: 0
});

// 核对各集合文档数量
db.books.countDocuments();
db.readers.countDocuments();
db.borrow_logs.countDocuments();


// ========== 任务三：检索功能实现 ==========

// --- 基础检索 Q1-Q6 ---

// Q1: 查找定价在 80 元以上的图书
db.books.find({ price: { $gt: 80 } });
db.books.countDocuments({ price: { $gt: 80 } });

// Q2: 查找库存不足 10 本的图书
db.books.find({ stock: { $lt: 10 } });
db.books.countDocuments({ stock: { $lt: 10 } });

// Q3: 按 ISBN 精确查找
db.books.find({ isbn: { $eq: "9787115428028" } });

// Q4: 查找 email 为空的读者
db.readers.find({ email: { $eq: null } });
db.readers.countDocuments({ email: { $eq: null } });

// Q5: 排除某个出版社的图书
db.books.find({ publisher: { $ne: "人民邮电出版社" } });

// Q6: 属于"计算机"或"经济管理"类别的图书
db.books.find({ category: { $in: ["计算机", "经济管理"] } });
db.books.countDocuments({ category: { $in: ["计算机", "经济管理"] } });


// --- 组合与高级检索 Q7-Q12 ---

// Q7: 评分 4.0 以上且属于计算机类
db.books.find({
  $and: [
    { rating: { $gte: 4.0 } },
    { category: "计算机" }
  ]
});

// Q8: 评分低于 3.5 或库存为 0
db.books.find({
  $or: [
    { rating: { $lt: 3.5 } },
    { stock: 0 }
  ]
});

// Q9: 书名包含 "Python"
db.books.find({ title: { $regex: "Python" } });

// Q10: 同时带有"编程"和"入门"两个标签
db.books.find({ tags: { $all: ["编程", "入门"] } });

// Q11: 恰好有 3 个标签的图书
db.books.find({ tags: { $size: 3 } });

// Q12: 查询已录入 tags 字段的图书
db.books.find({ tags: { $exists: true } });


// --- 结果处理 Q13-Q16 ---

// Q13: 查找 _id 为字符串类型的文档
db.books.find({ _id: { $type: "string" } });

// Q14: 按评分降序，取前 5 条
db.books.find().sort({ rating: -1 }).limit(5);

// Q15: 只返回书名、价格、评分（不含 _id）
db.books.find({}, { title: 1, price: 1, rating: 1, _id: 0 });

// Q16: 获取所有图书类别清单
db.books.distinct("category");


// --- 更新与删除 U1-U4、D1-D3 ---

// U1: 把某本图书的库存减少 5
db.books.updateOne(
  { isbn: "9787115428028" },
  { $inc: { stock: -5 } }
);

// U2: 将"计算机"类所有图书价格打 9 折
db.books.updateMany(
  { category: "计算机" },
  { $mul: { price: 0.9 } }
);

// U3: 为图书新增字段并自动记录当前时间
db.books.updateOne(
  { isbn: "9787115428028" },
  { $currentDate: { last_modified: true } }
);

// U4: 删除某本图书的 tags 字段
db.books.updateOne(
  { isbn: "9787115428028" },
  { $unset: { tags: "" } }
);

// D1: 删除一条已归还的借阅记录
db.borrow_logs.deleteOne({ status: "已归还" });

// D2: 清理逾期未还的借阅记录（先预览）
db.borrow_logs.find({ status: "逾期" });
db.borrow_logs.deleteMany({ status: "逾期" });

// D3: 整体替换某位读者的信息
db.readers.replaceOne(
  { card_no: "R20240001" },
  {
    card_no: "R20240001",
    name: "张明（更新）",
    college: "计算机学院",
    email: "zhangming_new@example.edu",
    phone: "13800138000",
    level: "高级",
    register_date: new Date("2024-09-01"),
    fav_categories: ["计算机", "文学"]
  }
);


// ========== 任务四：统计分析与权限管理 ==========

// --- 聚合管道 A1-A9 ---

// A1: 按类别统计图书数量与平均评分
db.books.aggregate([
  {
    $group: {
      _id: "$category",
      book_count: { $sum: 1 },
      avg_rating: { $avg: "$rating" }
    }
  }
]);

// A2: 各出版社图书数量 Top5
db.books.aggregate([
  { $group: { _id: "$publisher", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 5 }
]);

// A3: 文档数最多的图书类别（$sortByCount）
db.books.aggregate([
  { $sortByCount: "$category" }
]);

// A4: 评分最高的 3 本图书
db.books.aggregate([
  { $sort: { rating: -1 } },
  { $limit: 3 },
  { $project: { title: 1, rating: 1, borrow_count: 1, _id: 0 } }
]);

// A5: 每本书的销售额（单价 × 借阅次数）
db.books.aggregate([
  {
    $project: {
      title: 1,
      sales: { $round: [{ $multiply: ["$price", "$borrow_count"] }, 2] }
    }
  }
]);

// A6: 按借阅年份分组统计
db.borrow_logs.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y年", date: "$borrow_date" } },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
]);

// A7: 每位读者的借阅次数 Top5
db.borrow_logs.aggregate([
  { $group: { _id: "$reader_card", times: { $sum: 1 } } },
  { $sort: { times: -1 } },
  { $limit: 5 }
]);

// A8: 关联读者与借阅流水，学院借阅量排行
db.borrow_logs.aggregate([
  {
    $lookup: {
      from: "readers",
      localField: "reader_card",
      foreignField: "card_no",
      as: "reader"
    }
  },
  { $unwind: "$reader" },
  { $group: { _id: "$reader.college", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);

// A9: 把 A1 结果写入 category_stats 集合
db.books.aggregate([
  {
    $group: {
      _id: "$category",
      book_count: { $sum: 1 },
      avg_rating: { $avg: "$rating" }
    }
  },
  { $merge: "category_stats" }
]);


// --- 索引建立 I1-I5 ---

// I1: books.isbn 唯一索引
db.books.createIndex({ isbn: 1 }, { unique: true });

// I2: books.title 单键索引
db.books.createIndex({ title: 1 });

// I3: books.category 单键索引
db.books.createIndex({ category: 1 });

// I4: books.tags 多键索引
db.books.createIndex({ tags: 1 });

// I5: category + price 复合索引
db.books.createIndex({ category: 1, price: 1 });

// 查看所有索引
db.books.getIndexes();

// explain 对比查询耗时
db.books.find({ isbn: "9787115428028" }).explain("executionStats");


// --- 用户与权限 S1-S3 ---

// 注意：需要先在 admin 数据库下创建用户
use admin;

// S1: 创建只读账号 libReader
db.createUser({
  user: "libReader",
  pwd: readPasswordPrompt("输入只读账号密码: "),
  roles: [{ role: "read", db: "library" }]
});

// S2: 创建读写账号 libWriter
db.createUser({
  user: "libWriter",
  pwd: readPasswordPrompt("输入读写账号密码: "),
  roles: [
    { role: "readWrite", db: "library" },
    { role: "dbAdmin", db: "library" }
  ]
});

// S3: 验证权限（重启服务后加 --auth 参数，再用以下命令测试）
// mongosh -u libReader -p --authenticationDatabase library
// > use library
// > db.books.find()        // 读操作成功
// > db.books.insertOne({}) // 写操作被拒绝
