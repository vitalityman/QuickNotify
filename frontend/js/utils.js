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