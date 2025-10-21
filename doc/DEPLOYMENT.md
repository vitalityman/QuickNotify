# QuickNotify 开发指南

## 环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/vitalityman/QuickNotify.git
cd QuickNotify
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
```

### 4. 运行应用
```bash
python app.py
```

## 代码结构

### Backend 后端目录

```
backend/
├── app.py                 # Flask主应用
├── config.py              # 配置管理
├── requirements.txt       # Python依赖
├── models/
│   ├── database.py        # 数据库初始化
│   └── models.py          # 数据模型
├── routes/
│   ├── auth.py            # 认证接口
│   ├── config.py          # 配置接口
│   ├── template.py        # 模板接口
│   ├── sender.py          # 发送接口
│   ├── records.py         # 记录接口
│   └── monitor.py         # 监控接口
└── utils/
    ├── mail_sender.py     # 邮件发送
    ├── crypto.py          # 加密解密
    └── log_handler.py     # 日志处理
```

### Frontend 前端目录

```
frontend/
├── index.html             # 单页应用主入口
├── css/
│   └── style.css          # 全局样式
└── js/
    ├── api.js             # API调用封装
    ├── main.js            # 应用主逻辑
    └── utils.js           # 工具函数
```

## 常见开发任务

### 测试API

```bash
# 测试登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 测试发送邮件
curl -X POST http://localhost:5000/api/sender/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipients":["test@example.com"],
    "subject":"Test",
    "content":"Hello World"
  }'
```

## 调试技巧

### 启用调试模式

在 `config.py` 中设置 `DEBUG = True`

### 查看日志

```bash
tail -f logs/app.log
```

### 检查数据库

```bash
sqlite3 backend/quicknotify.db
SELECT * FROM email_templates;
```

## 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

More information: [README.md](../README.md)