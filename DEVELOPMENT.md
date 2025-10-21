# QuickNotify 开发指南

## 快速开始

### 环境设置

1. **克隆项目**
```bash
git clone https://github.com/vitalityman/QuickNotify.git
cd QuickNotify
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
cd backend
pip install -r requirements.txt
```

4. **运行应用**
```bash
cd backend
python app.py
```

访问 http://localhost:5000

## 项目结构说明

```
QuickNotify/
├── backend/                 # 后端Flask应用
│   ├── app.py              # 主应用入口
│   ├── config.py           # 配置管理
│   ├── requirements.txt    # 后端依赖
│   ├── models/             # 数据模型
│   │   ├── database.py
│   │   └── models.py
│   ├── routes/             # API路由
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── template.py
│   │   ├── sender.py
│   │   ├── records.py
│   │   └── monitor.py
│   └── utils/              # 工具函数
│       ├── mail_sender.py
│       ├── crypto.py
│       └── log_handler.py
├── frontend/               # 前端SPA应用
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js
│       ├── main.js
│       └── utils.js
└── docs/                   # 文档
```

## 代码规范

### Python代码风格

- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 函数和类之间使用两个空行分隔
- 变量名使用 snake_case
- 类名使用 PascalCase

## 常见开发任务

### 添加新API端点

```python
# backend/routes/new_feature.py
from flask import Blueprint, jsonify, request, session

new_bp = Blueprint('new_feature', __name__)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

@new_bp.route('/endpoint', methods=['GET'])
@login_required
def get_endpoint():
    return jsonify({'data': 'value'}), 200

# backend/app.py - 注册蓝图
from routes.new_feature import new_bp
app.register_blueprint(new_bp, url_prefix='/api/new_feature')
```

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

### 启用Flask调试模式
在 `backend/config.py` 中设置 `DEBUG = True`

### 查看应用日志
```bash
tail -f logs/app.log
```

### 使用数据库
```bash
# 打开SQLite数据库
sqlite3 backend/quicknotify.db

# 查看表
.tables

# 查询数据
SELECT * FROM users;
```

## 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 常见问题

**Q: 如何重置数据库？**
A: 删除 `backend/quicknotify.db` 文件后重启应用

**Q: 如何查看API文档？**
A: 查看 `API_EXAMPLES.md` 文件

---

More information: [README.md](README.md)