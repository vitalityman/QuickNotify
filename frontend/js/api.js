class QuickNotifyAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    async request(method, endpoint, data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        if (data) config.data = JSON.stringify(data);
        
        try {
            const response = await axios(url, config);
            return response.data;
        } catch (error) {
            if (error.response?.status === 401) {
                window.location.href = '/';
            }
            throw error.response?.data || error.message;
        }
    }

    // 认证接口
    login(username, password) {
        return this.request('POST', '/auth/login', { username, password });
    }

    logout() {
        return this.request('POST', '/auth/logout');
    }

    checkAuth() {
        return this.request('GET', '/auth/check');
    }

    // 配置接口
    getSMTPConfig() {
        return this.request('GET', '/config/smtp');
    }

    updateSMTPConfig(config) {
        return this.request('POST', '/config/smtp', config);
    }

    testSMTP() {
        return this.request('POST', '/config/smtp/test');
    }

    // 模板接口
    listTemplates(page = 1, perPage = 10, search = '') {
        return this.request('GET', `/template/?page=${page}&per_page=${perPage}&search=${search}`);
    }

    getTemplate(id) {
        return this.request('GET', `/template/${id}`);
    }

    createTemplate(template) {
        return this.request('POST', '/template/', template);
    }

    updateTemplate(id, template) {
        return this.request('PUT', `/template/${id}`, template);
    }

    deleteTemplate(id) {
        return this.request('DELETE', `/template/${id}`);
    }

    // 发送接口
    sendEmail(recipients, subject, content, cc = [], bcc = []) {
        return this.request('POST', '/sender/send', {
            recipients, subject, content, cc, bcc
        });
    }

    sendFromTemplate(templateId, recipients, variables, cc = [], bcc = []) {
        return this.request('POST', '/sender/send-from-template', {
            template_id: templateId,
            recipients, variables, cc, bcc
        });
    }

    // 记录接口
    listRecords(page = 1, perPage = 20, status = 'all') {
        return this.request('GET', `/records/?page=${page}&per_page=${perPage}&status=${status}`);
    }

    getRecordStats() {
        return this.request('GET', '/records/stats');
    }

    retryRecord(id) {
        return this.request('POST', `/records/${id}/retry`);
    }

    // 监控接口
    getSystemStatus() {
        return this.request('GET', '/monitor/status');
    }

    getSystemLogs(level = 'ALL') {
        return this.request('GET', `/monitor/logs?level=${level}`);
    }

    getDailyStats() {
        return this.request('GET', '/monitor/stats/daily');
    }
}

const api = new QuickNotifyAPI();