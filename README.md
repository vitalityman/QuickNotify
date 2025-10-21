# QuickNotify - 轻量级邮件通知系统

QuickNotify 是一款轻量级、可快速部署在服务器的邮件通知系统，核心功能是在指定指令/操作完成后，自动向预设接收人发送定制化邮件通知。支持Web图形化界面、CLI命令行、脚本集成等多种使用方式。

## ✨ 核心功能

- 🚀 **快速部署** - Docker一键部署，5分钟内完成服务器部署
- 📧 **灵活触发** - 支持命令行、脚本集成、Web界面手动触发
- 📝 **模板管理** - 支持邮件模板、动态变量替换、Markdown格式
- 🌐 **Web界面** - 可视化配置、发送记录查询、服务监控
- 📊 **数据统计** - 实时统计发送数据、成功率分析
- 🔐 **安全可靠** - SMTP加密存储、失败重试、状态记录

## 📋 系统要求

- Python 3.9+ 或 Docker
- Linux/macOS/Windows
- SMTP邮件服务器

## 🚀 快速开始

### Docker部署（推荐）

```bash
# 克隆项目
git clone https://github.com/vitalityman/QuickNotify.git
cd QuickNotify

# 启动应用
docker-compose up -d

# 访问 http://localhost:5000
# 默认账号：admin，密码：123456
```

### 本地运行

```bash
# 安装依赖
bash install.sh

# 启动应用
bash start.sh

# 访问 http://localhost:5000
```

## 📖 快速使用

### Web界面使用

1. 登录系统（默认 admin/123456）
2. 配置SMTP服务器信息
3. 创建邮件模板（支持变量替换）
4. 发送邮件或查看发送历史

### CLI命令行

```bash
# 直接发送邮件
python quicknotify_cli.py send --to user@example.com --subject "Test" --content "Hello"

# 查看所有模板
python quicknotify_cli.py template list

# 测试SMTP连接
python quicknotify_cli.py config test

# 查看发送记录
python quicknotify_cli.py records --status success
```

### 脚本集成（Python）

```python
import requests

response = requests.post('http://localhost:5000/api/sender/send', json={
    'recipients': ['user@example.com'],
    'subject': 'Task Complete',
    'content': 'Your task has completed successfully'
})
```

### 脚本集成（Shell）

```bash
#!/bin/bash

curl -X POST http://localhost:5000/api/sender/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user@example.com"],
    "subject": "Backup Complete",
    "content": "Database backup completed at '$(date)'"
  }'
```

## 📁 项目结构

```
QuickNotify/
├── backend/                 # 后端应用
│   ├── app.py              # Flask主应用
│   ├── config.py           # 配置管理
│   ├── requirements.txt    # Python依赖
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   ├── utils/              # 工具函数
│   └── logs/               # 日志目录
├── frontend/               # 前端应用
│   ├── index.html          # 主页面
│   ├── css/                # 样式表
│   └── js/                 # JavaScript
├── docs/                   # 文档目录
├── .env.example            # 环境变量模板
├── Dockerfile              # Docker构建
├── docker-compose.yml      # Docker编排
├── nginx.conf              # Nginx配置
├── quicknotify_cli.py      # CLI工具
├── README.md               # 项目文档
├── DEVELOPMENT.md          # 开发指南
└── API_EXAMPLES.md         # API示例
```

## 🌐 API文档

### 认证接口

```
POST   /api/auth/login              # 登录
POST   /api/auth/logout             # 登出
GET    /api/auth/check              # 检查认证
```

### 配置接口

```
GET    /api/config/smtp             # 获取SMTP配置
POST   /api/config/smtp             # 更新SMTP配置
POST   /api/config/smtp/test        # 测试SMTP连接
```

### 模板接口

```
GET    /api/template/               # 列出模板
POST   /api/template/               # 创建模板
GET    /api/template/<id>           # 获取模板详情
PUT    /api/template/<id>           # 更新模板
DELETE /api/template/<id>           # 删除模板
```

### 发送接口

```
POST   /api/sender/send             # 直接发送邮件
POST   /api/sender/send-from-template  # 使用模板发送
```

### 记录接口

```
GET    /api/records/                # 列出发送记录
GET    /api/records/<id>            # 获取记录详情
POST   /api/records/<id>/retry      # 重试发送
DELETE /api/records/<id>            # 删除记录
GET    /api/records/stats           # 获取统计数据
```

### 监控接口

```
GET    /api/monitor/status          # 系统状态
GET    /api/monitor/logs            # 系统日志
GET    /api/monitor/stats/daily     # 日统计
GET    /api/monitor/stats/sources   # 来源统计
```

## ⚙️ 环境配置

编辑 `.env` 文件配置：

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///quicknotify.db
INIT_USER=admin
INIT_PWD=123456
PORT=5000
DEBUG=True
```

## 📊 性能指标

- 内存占用: ≤ 100MB
- CPU占用: ≤ 5%（空闲时）
- 页面加载: ≤ 2秒
- 邮件发送: ≤ 5秒

## 🔒 安全特性

- ✅ 密码加密存储（Fernet加密）
- ✅ Session会话管理（30分钟超时）
- ✅ 登录验证保护
- ✅ HTTPS支持（Nginx）

## 📝 常见问题

**Q: 如何修改默认密码？**
A: 在Web界面登录后修改。

**Q: SMTP连接失败？**
A: 检查SMTP配置是否正确。

**Q: 如何备份数据？**
A: 备份 `quicknotify.db` 数据库文件。

**Q: 支持多用户吗？**
A: 当前为单用户，可自行扩展。

## 🚀 生产部署

```bash
# 使用Nginx反向代理和HTTPS
docker-compose up -d
# 配置Nginx和SSL证书
# 访问 https://your-domain.com
```

## 📚 文档链接

- [开发指南](DEVELOPMENT.md)
- [API示例](API_EXAMPLES.md)
- [部署文档](docs/DEPLOYMENT.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

遇到问题？请提交Issue或查看文档。

---

**Made with ❤️ by QuickNotify Team**