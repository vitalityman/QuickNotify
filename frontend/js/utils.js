// 工具函数集合

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

function parseEmails(text) {
    return text
        .split('\n')
        .map(email => email.trim())
        .filter(email => email && email.includes('@'));
}

function getStatusBadge(status) {
    const statusMap = {
        'success': { text: '✅ 成功', class: 'success' },
        'failed': { text: '❌ 失败', class: 'failed' }
    };
    const info = statusMap[status] || { text: status, class: '' };
    return `<span class="status-badge ${info.class}">${info.text}</span>`;
}

function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 获取状态徽章
function getStatusBadge(status) {
    if (status === 'success') {
        return '<span style="color: green;">✅ 成功</span>';
    } else if (status === 'failed') {
        return '<span style="color: red;">❌ 失败</span>';
    }
    return status;
}

// 解析邮箱列表
function parseEmails(text) {
    return text
        .split('\n')
        .map(email => email.trim())
        .filter(email => email && email.includes('@'));
}

// HTML转义（防止XSS）
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 显示通知提示
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}