let currentUser = null;
let currentPage = 'dashboard';

// 页面初始化
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await api.checkAuth();
        showMainPage();
    } catch {
        showLoginPage();
    }

    setupEventListeners();
});

function showLoginPage() {
    document.getElementById('login-page').classList.add('active');
    document.getElementById('main-page').classList.remove('active');
}

function showMainPage() {
    document.getElementById('login-page').classList.remove('active');
    document.getElementById('main-page').classList.add('active');
}

function setupEventListeners() {
    // 登录
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            await api.login(username, password);
            currentUser = username;
            document.getElementById('current-user').textContent = username;
            showMainPage();
            loadDashboard();
        } catch (error) {
            showNotification('登录失败：' + (error.error || '未知错误'), 'error');
        }
    });

    // 登出
    document.getElementById('logout-btn').addEventListener('click', async () => {
        try {
            await api.logout();
            showLoginPage();
        } catch (error) {
            console.error(error);
        }
    });

    // 导航菜单
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            switchPage(page);
        });
    });

    // SMTP配置
    document.getElementById('smtp-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const config = {
            smtp_server: document.getElementById('smtp-server').value,
            smtp_port: parseInt(document.getElementById('smtp-port').value),
            sender_email: document.getElementById('sender-email').value,
            sender_password: document.getElementById('sender-password').value,
            use_tls: true
        };
        
        try {
            await api.updateSMTPConfig(config);
            showNotification('SMTP配置保存成功', 'success');
        } catch (error) {
            showNotification('保存失败：' + (error.error || '未知错误'), 'error');
        }
    });

    // 测试SMTP
    document.getElementById('test-smtp').addEventListener('click', async () => {
        try {
            const result = await api.testSMTP();
            showNotification(result.message, result.success ? 'success' : 'error');
        } catch (error) {
            showNotification('测试失败：' + (error.error || '未知错误'), 'error');
        }
    });

    // 发送邮件
    document.getElementById('send-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const recipients = parseEmails(document.getElementById('send-recipients').value);
        const subject = document.getElementById('send-subject').value;
        const content = document.getElementById('send-content').value;
        
        if (!recipients.length) {
            showNotification('请输入至少一个收件人', 'error');
            return;
        }
        
        try {
            const result = await api.sendEmail(recipients, subject, content);
            showNotification(result.message, result.success ? 'success' : 'error');
            if (result.success) {
                document.getElementById('send-form').reset();
            }
        } catch (error) {
            showNotification('发送失败：' + (error.error || '未知错误'), 'error');
        }
    });

    // 查询记录
    document.getElementById('query-records').addEventListener('click', loadRecords);

    // 快速操作
    document.getElementById('quick-send').addEventListener('click', () => switchPage('sender'));
    document.getElementById('quick-template').addEventListener('click', () => switchPage('template'));
    document.getElementById('quick-config').addEventListener('click', () => switchPage('config'));
}

function switchPage(page) {
    currentPage = page;
    
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    document.querySelectorAll('.content-page').forEach(p => p.classList.remove('active'));
    document.getElementById(`${page}-page`).classList.add('active');
    
    if (page === 'dashboard') {
        loadDashboard();
    } else if (page === 'template') {
        loadTemplates();
    } else if (page === 'records') {
        loadRecords();
    } else if (page === 'monitor') {
        loadMonitor();
    }
}

async function loadDashboard() {
    try {
        const stats = await api.getRecordStats();
        document.getElementById('today-total').textContent = stats.today.total;
        document.getElementById('today-success').textContent = stats.today.success;
        document.getElementById('today-failed').textContent = stats.today.failed;
        document.getElementById('total-all').textContent = stats.total.total;
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

async function loadTemplates() {
    try {
        const data = await api.listTemplates();
        const tbody = document.getElementById('template-tbody');
        tbody.innerHTML = data.templates.map(t => `
            <tr>
                <td>${t.name}</td>
                <td>${t.subject}</td>
                <td>${formatDate(t.created_at)}</td>
                <td>
                    <button class="btn btn-small">编辑</button>
                    <button class="btn btn-small">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load templates:', error);
    }
}

async function loadRecords() {
    try {
        const status = document.getElementById('status-filter').value;
        const data = await api.listRecords(1, 20, status);
        const tbody = document.getElementById('record-tbody');
        tbody.innerHTML = data.records.map(r => `
            <tr>
                <td>${formatDateTime(r.created_at)}</td>
                <td>${r.recipients.join(', ')}</td>
                <td>${r.subject}</td>
                <td>${getStatusBadge(r.status)}</td>
                <td><button class="btn btn-small">详情</button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load records:', error);
    }
}

async function loadMonitor() {
    try {
        const status = await api.getSystemStatus();
        document.getElementById('cpu-percent').textContent = status.cpu_percent.toFixed(1) + '%';
        document.getElementById('memory-percent').textContent = status.memory.percent.toFixed(1) + '%';
        document.getElementById('process-memory').textContent = status.process.memory_mb.toFixed(1) + ' MB';
        
        const logs = await api.getSystemLogs('ALL', 50);
        document.getElementById('logs-content').innerHTML = logs.logs.map(log => `<div>${log}</div>`).join('');
    } catch (error) {
        console.error('Failed to load monitor data:', error);
    }
}