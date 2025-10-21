# QuickNotify API 示例集合

## 认证接口

### 登录
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

**响应 (200):**
```json
{
  "message": "Login successful",
  "username": "admin"
}
```

### 登出
```bash
curl -X POST http://localhost:5000/api/auth/logout
```

### 检查认证状态
```bash
curl -X GET http://localhost:5000/api/auth/check
```

**响应 (200):**
```json
{
  "authenticated": true,
  "username": "admin"
}
```

## 配置接口

### 获取SMTP配置
```bash
curl -X GET http://localhost:5000/api/config/smtp
```

### 更新SMTP配置
```bash
curl -X POST http://localhost:5000/api/config/smtp \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "noreply@example.com",
    "sender_password": "your_password",
    "use_tls": true
  }'
```

**响应 (200):**
```json
{
  "message": "SMTP configuration saved"
}
```

### 测试SMTP连接
```bash
curl -X POST http://localhost:5000/api/config/smtp/test
```

**响应 (200):**
```json
{
  "success": true,
  "message": "SMTP connection successful"
}
```

## 模板接口

### 列出所有模板
```bash
curl -X GET "http://localhost:5000/api/template/?page=1&per_page=10&search="
```

**响应 (200):**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Task Completed",
      "subject": "Task {{task_name}} completed",
      "created_at": "2025-10-21T03:20:00",
      "variables": ["task_name", "duration"]
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### 创建模板
```bash
curl -X POST http://localhost:5000/api/template/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Task Completed",
    "subject": "Task {{task_name}} completed",
    "content": "Your task **{{task_name}}** has completed!"
  }'
```

**响应 (201):**
```json
{
  "message": "Template created successfully",
  "id": 1
}
```

### 删除模板
```bash
curl -X DELETE http://localhost:5000/api/template/1
```

## 发送接口

### 直接发送邮件
```bash
curl -X POST http://localhost:5000/api/sender/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user@example.com"],
    "subject": "Test Email",
    "content": "Hello World",
    "cc": [],
    "bcc": []
  }'
```

**响应 (200):**
```json
{
  "message": "Email sent to 1 recipients",
  "success": true,
  "record_id": 1,
  "duration": 2
}
```

### 使用模板发送
```bash
curl -X POST http://localhost:5000/api/sender/send-from-template \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "recipients": ["user@example.com"],
    "variables": {
      "task_name": "Data Export",
      "duration": "5 minutes"
    }
  }'
```

## 记录接口

### 列出发送记录
```bash
curl -X GET "http://localhost:5000/api/records/?page=1&per_page=20&status=all"
```

### 获取发送统计
```bash
curl -X GET http://localhost:5000/api/records/stats
```

**响应 (200):**
```json
{
  "today": {
    "total": 10,
    "success": 8,
    "failed": 2,
    "success_rate": 80.0
  },
  "week": {
    "total": 50,
    "success": 45,
    "failed": 5,
    "success_rate": 90.0
  },
  "total": {
    "total": 500,
    "success": 480,
    "failed": 20,
    "success_rate": 96.0
  }
}
```

## 监控接口

### 系统状态
```bash
curl -X GET http://localhost:5000/api/monitor/status
```

**响应 (200):**
```json
{
  "status": "running",
  "cpu_percent": 5.2,
  "memory": {
    "total": 8.0,
    "used": 3.5,
    "percent": 43.75
  },
  "process": {
    "memory_mb": 75.5,
    "cpu_percent": 1.2
  },
  "timestamp": "2025-10-21T03:25:00"
}
```

### 系统日志
```bash
curl -X GET "http://localhost:5000/api/monitor/logs?level=ALL&lines=50"
```

---

See [README.md](README.md) for more information.