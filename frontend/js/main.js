let currentUser = null;
let currentPage = 'dashboard';

// 页面初始化
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Page loaded, checking authentication...');
    
    try {
        const authResponse = await api.checkAuth();
        console.log('Auth check response:', authResponse);
        
        if (authResponse.authenticated) {
            currentUser = authResponse.username;
            console.log('User authenticated:', currentUser);
            showMainPage();
            await loadDashboard();
        } else {
            console.log('User not authenticated, showing login page');
            showLoginPage();
        }
    } catch (error) {
        console.log('Auth check failed, showing login page:', error);
        showLoginPage();
    }

    setupEventListeners();
    console.log('Event listeners set up complete');
});

function showLoginPage() {
    console.log('Showing login page');
    const loginPage = document.getElementById('login-page');
    const mainPage = document.getElementById('main-page');
    
    if (loginPage) loginPage.classList.add('active');
    if (mainPage) mainPage.classList.remove('active');
}

function showMainPage() {
    console.log('Showing main page');
    const loginPage = document.getElementById('login-page');
    const mainPage = document.getElementById('main-page');
    
    if (loginPage) loginPage.classList.remove('active');
    if (mainPage) mainPage.classList.add('active');
    
    if (currentUser) {
        const userDisplay = document.getElementById('current-user');
        if (userDisplay) {
            userDisplay.textContent = currentUser;
        }
    }
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // ========== 登录表单 ==========
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        console.log('Login form found, attaching submit event');
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Login form submitted');
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            console.log('Attempting login with username:', username);
            
            try {
                const loginResponse = await api.login(username, password);
                console.log('Login response:', loginResponse);
                
                currentUser = username;
                document.getElementById('current-user').textContent = username;
                
                console.log('Login successful, showing main page');
                showMainPage();
                
                console.log('Loading dashboard...');
                await loadDashboard();
                
                showNotification('✅ 登录成功！', 'success');
                console.log('Login process complete');
            } catch (error) {
                console.error('Login error:', error);
                showNotification('❌ 登录失败：' + (error.error || '未知错误'), 'error');
            }
        });
    } else {
        console.warn('Login form not found!');
    }

    // ========== 登出按钮 ==========
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        console.log('Logout button found, attaching click event');
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            console.log('Logout button clicked');
            try {
                await api.logout();
                console.log('Logout successful');
                showLoginPage();
                showNotification('✅ 已登出', 'success');
            } catch (error) {
                console.error('Logout error:', error);
                showNotification('❌ 登出失败', 'error');
            }
        });
    }

    // ========== 导航菜单 ==========
    const navItems = document.querySelectorAll('.nav-item');
    console.log('Found', navItems.length, 'nav items');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            console.log('Navigation clicked, switching to page:', page);
            switchPage(page);
        });
    });

    // ========== SMTP配置表单 ==========
    const smtpForm = document.getElementById('smtp-form');
    if (smtpForm) {
        console.log('SMTP form found');
        loadSMTPConfig();

        smtpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('SMTP form submitted');
            
            const config = {
                smtp_server: document.getElementById('smtp-server').value,
                smtp_port: parseInt(document.getElementById('smtp-port').value),
                sender_email: document.getElementById('sender-email').value,
                sender_password: document.getElementById('sender-password').value,
                use_tls: true
            };

            if (!config.smtp_server || !config.smtp_port || !config.sender_email || !config.sender_password) {
                showNotification('❌ 请填写所有必填字段', 'error');
                return;
            }

            try {
                await api.updateSMTPConfig(config);
                showNotification('✅ SMTP配置保存成功！', 'success');
                console.log('SMTP config saved');
            } catch (error) {
                console.error('Save error:', error);
                showNotification('❌ 保存失败：' + (error.error || '未知错误'), 'error');
            }
        });
    }

    // ========== 测试SMTP按钮 ==========
    const testSmtpBtn = document.getElementById('test-smtp');
    if (testSmtpBtn) {
        console.log('Test SMTP button found');
        testSmtpBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            console.log('Testing SMTP connection...');
            showNotification('⏳ 正在测试SMTP连接...', 'info');
            
            try {
                const result = await api.testSMTP();
                console.log('SMTP test result:', result);
                if (result.success) {
                    showNotification('✅ ' + result.message, 'success');
                } else {
                    showNotification('❌ ' + result.message, 'error');
                }
            } catch (error) {
                console.error('Test error:', error);
                showNotification('❌ 测试失败：' + (error.error || '未知错误'), 'error');
            }
        });
    }

    // ========== 发送邮件表单 ==========
    const sendForm = document.getElementById('send-form');
    if (sendForm) {
        console.log('Send form found');
        sendForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Send form submitted');
            
            const recipients = parseEmails(document.getElementById('send-recipients').value);
            const subject = document.getElementById('send-subject').value;
            const content = document.getElementById('send-content').value;
            
            if (!recipients.length) {
                showNotification('❌ 请输入至少一个收件人', 'error');
                return;
            }
            
            if (!subject || !content) {
                showNotification('❌ 请填写主题和内容', 'error');
                return;
            }
            
            try {
                const result = await api.sendEmail(recipients, subject, content);
                console.log('Send result:', result);
                if (result.success) {
                    showNotification('✅ ' + result.message, 'success');
                    document.getElementById('send-form').reset();
                } else {
                    showNotification('❌ ' + result.message, 'error');
                }
            } catch (error) {
                console.error('Send error:', error);
                showNotification('❌ 发送失败：' + (error.error || '未知错误'), 'error');
            }
        });
    }

    // ========== 查询记录按钮 ==========
    const queryRecordsBtn = document.getElementById('query-records');
    if (queryRecordsBtn) {
        queryRecordsBtn.addEventListener('click', () => {
            console.log('Query records button clicked');
            loadRecords();
        });
    }

    // ========== 快速操作按钮 ==========
    const quickSendBtn = document.getElementById('quick-send');
    if (quickSendBtn) {
        quickSendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Quick send button clicked');
            switchPage('sender');
        });
    }

    const quickTemplateBtn = document.getElementById('quick-template');
    if (quickTemplateBtn) {
        quickTemplateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Quick template button clicked');
            switchPage('template');
        });
    }

    const quickConfigBtn = document.getElementById('quick-config');
    if (quickConfigBtn) {
        quickConfigBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Quick config button clicked');
            switchPage('config');
        });
    }

    // ========== 新建模板按钮 ==========
    const newTemplateBtn = document.getElementById('new-template');
    if (newTemplateBtn) {
        console.log('New template button found');
        newTemplateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('New template button clicked, opening modal');
            openTemplateModal();
        });
    } else {
        console.warn('New template button not found!');
    }

    // ========== 模板表单 ==========
    const templateForm = document.getElementById('template-form');
    if (templateForm) {
        console.log('Template form found');
        templateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Template form submitted');
            
            const templateData = {
                name: document.getElementById('template-name').value,
                subject: document.getElementById('template-subject').value,
                content: document.getElementById('template-content').value
            };
            
            if (!templateData.name || !templateData.subject || !templateData.content) {
                showNotification('❌ 请填写所有必填字段', 'error');
                return;
            }
            
            try {
                const result = await api.createTemplate(templateData);
                console.log('Template created:', result);
                showNotification('✅ 模板创建成功！', 'success');
                closeTemplateModal();
                await loadTemplates();
                templateForm.reset();
            } catch (error) {
                console.error('Create template error:', error);
                showNotification('❌ 创建失败：' + (error.error || '未知错误'), 'error');
            }
        });
    }

    // ========== 模态框关闭按钮 ==========
    const closeBtn = document.querySelector('.modal .close');
    if (closeBtn) {
        console.log('Modal close button found');
        closeBtn.addEventListener('click', closeTemplateModal);
    }

    // ========== 模态框取消按钮 ==========
    const cancelBtn = document.querySelector('.modal .cancel-btn');
    if (cancelBtn) {
        console.log('Modal cancel button found');
        cancelBtn.addEventListener('click', closeTemplateModal);
    }

    // ========== 模态框外部点击关闭 ==========
    const modal = document.getElementById('template-modal');
    if (modal) {
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeTemplateModal();
            }
        });
    }

    // ========== 发送模式选择 ==========
    console.log('Setting up send mode buttons...');
    const modeBtns = document.querySelectorAll('.mode-btn');
    console.log('Found', modeBtns.length, 'mode buttons');

    if (modeBtns.length === 0) {
        console.warn('No mode buttons found!');
    }

    modeBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const mode = btn.dataset.mode;
            console.log('Mode button clicked, mode:', mode);
            
            // 更新按钮状态
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 显示对应的模式内容
            const directMode = document.getElementById('direct-send-mode');
            const templateMode = document.getElementById('template-send-mode');
            
            if (directMode) directMode.classList.remove('active');
            if (templateMode) templateMode.classList.remove('active');
            
            if (mode === 'direct') {
                console.log('Showing direct send mode');
                if (directMode) {
                    directMode.classList.add('active');
                }
            } else if (mode === 'template') {
                console.log('Showing template send mode');
                if (templateMode) {
                    templateMode.classList.add('active');
                }
                
                // 立即加载模板列表
                console.log('Calling loadTemplateSelect...');
                await loadTemplateSelect();
            }
        });
    });

    // ========== 使用模板发送表单 ==========
    const sendTemplateForm = document.getElementById('send-template-form');
    console.log('Send template form:', sendTemplateForm);
    
    if (sendTemplateForm) {
        console.log('Attaching events to send template form');
        
        // 模板选择变化时
        const templateSelect = document.getElementById('template-select');
        console.log('Template select element:', templateSelect);
        
        if (templateSelect) {
            console.log('Attaching change event to template select');
            templateSelect.addEventListener('change', async (e) => {
                const templateId = e.target.value;
                console.log('Template select changed, templateId:', templateId);
                
                if (templateId) {
                    console.log('Loading preview for template:', templateId);
                    await loadTemplatePreview(templateId);
                } else {
                    console.log('No template selected');
                    document.getElementById('template-preview').innerHTML = '<p class="text-muted">选择模板后显示预览</p>';
                    document.getElementById('template-variables').innerHTML = '';
                }
            });
        } else {
            console.warn('Template select element NOT found!');
        }
        
        // 表单提交
        sendTemplateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Send template form submitted');
            
            const templateId = document.getElementById('template-select').value;
            const recipients = parseEmails(document.getElementById('template-recipients').value);
            
            if (!templateId) {
                showNotification('❌ 请选择模板', 'error');
                return;
            }
            
            if (!recipients.length) {
                showNotification('❌ 请输入至少一个收件人', 'error');
                return;
            }
            
            // 收集变量值
            const variables = {};
            const variableInputs = document.querySelectorAll('.template-variables input');
            variableInputs.forEach(input => {
                const name = input.dataset.variable;
                if (name) {
                    variables[name] = input.value;
                }
            });
            
            console.log('Sending template email with:', {
                templateId: templateId,
                recipients: recipients,
                variables: variables
            });
            
            try {
                const result = await api.sendFromTemplate(templateId, recipients, variables);
                console.log('Send template result:', result);
                if (result.success) {
                    showNotification('✅ ' + result.message, 'success');
                    document.getElementById('send-template-form').reset();
                    document.getElementById('template-variables').innerHTML = '';
                    document.getElementById('template-preview').innerHTML = '<p class="text-muted">选择模板后显示预览</p>';
                } else {
                    showNotification('❌ ' + result.message, 'error');
                }
            } catch (error) {
                console.error('Send template error:', error);
                showNotification('❌ 发送失败：' + (error.error || '未知错误'), 'error');
            }
        });
    } else {
        console.warn('Send template form NOT found!');
    }
}

// ========== 页面切换函数 ==========
function switchPage(page) {
    console.log('Switching to page:', page);
    currentPage = page;
    
    // 更新导航菜单
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeNav = document.querySelector(`[data-page="${page}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }
    
    // 显示对应的页面
    document.querySelectorAll('.content-page').forEach(p => {
        p.classList.remove('active');
    });
    const activePage = document.getElementById(`${page}-page`);
    if (activePage) {
        activePage.classList.add('active');
    }
    
    // 加载页面数据
    if (page === 'dashboard') {
        loadDashboard();
    } else if (page === 'config') {
        loadSMTPConfig();
    } else if (page === 'template') {
        loadTemplates();
    } else if (page === 'sender') {
        console.log('Loading sender page...');
        // 自动加载模板列表
        loadTemplateSelect();
    } else if (page === 'records') {
        loadRecords();
    } else if (page === 'monitor') {
        loadMonitor();
    }
}

// ========== 加载仪表板数据 ==========
async function loadDashboard() {
    console.log('Loading dashboard...');
    try {
        const stats = await api.getRecordStats();
        console.log('Dashboard stats loaded:', stats);
        
        const todayTotalEl = document.getElementById('today-total');
        const todaySuccessEl = document.getElementById('today-success');
        const todayFailedEl = document.getElementById('today-failed');
        const totalAllEl = document.getElementById('total-all');
        
        if (todayTotalEl) todayTotalEl.textContent = stats.today.total;
        if (todaySuccessEl) todaySuccessEl.textContent = stats.today.success;
        if (todayFailedEl) todayFailedEl.textContent = stats.today.failed;
        if (totalAllEl) totalAllEl.textContent = stats.total.total;
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// ========== 加载SMTP配置 ==========
async function loadSMTPConfig() {
    console.log('Loading SMTP config...');
    try {
        const config = await api.getSMTPConfig();
        console.log('SMTP config loaded:', config);
        
        if (config.smtp_server) {
            const serverEl = document.getElementById('smtp-server');
            const portEl = document.getElementById('smtp-port');
            const emailEl = document.getElementById('sender-email');
            
            if (serverEl) serverEl.value = config.smtp_server;
            if (portEl) portEl.value = config.smtp_port;
            if (emailEl) emailEl.value = config.sender_email;
        }
    } catch (error) {
        console.log('No SMTP config found:', error);
    }
}

// ========== 加载模板列表 ==========
async function loadTemplates() {
    console.log('Loading templates...');
    try {
        const data = await api.listTemplates();
        console.log('Templates loaded:', data);
        
        const tbody = document.getElementById('template-tbody');
        if (!tbody) {
            console.warn('template-tbody not found');
            return;
        }
        
        if (data.templates.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">暂无模板</td></tr>';
            return;
        }
        
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

// ========== 加载发送记录 ==========
async function loadRecords() {
    console.log('Loading records...');
    try {
        const statusFilter = document.getElementById('status-filter');
        const status = statusFilter ? statusFilter.value : 'all';
        
        const data = await api.listRecords(1, 20, status);
        console.log('Records loaded:', data);
        
        const tbody = document.getElementById('record-tbody');
        if (!tbody) {
            console.warn('record-tbody not found');
            return;
        }
        
        if (data.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">暂无记录</td></tr>';
            return;
        }
        
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

// ========== 加载监控数据 ==========
async function loadMonitor() {
    console.log('Loading monitor data...');
    try {
        const status = await api.getSystemStatus();
        console.log('System status:', status);
        
        const cpuEl = document.getElementById('cpu-percent');
        const memoryEl = document.getElementById('memory-percent');
        const processMemEl = document.getElementById('process-memory');
        
        if (cpuEl) cpuEl.textContent = status.cpu_percent.toFixed(1) + '%';
        if (memoryEl) memoryEl.textContent = status.memory.percent.toFixed(1) + '%';
        if (processMemEl) processMemEl.textContent = status.process.memory_mb.toFixed(1) + ' MB';
        
        const logs = await api.getSystemLogs('ALL', 50);
        console.log('System logs:', logs);
        
        const logsContent = document.getElementById('logs-content');
        if (logsContent) {
            logsContent.innerHTML = logs.logs.map(log => `<div>${log}</div>`).join('');
        }
    } catch (error) {
        console.error('Failed to load monitor data:', error);
    }
}

// ========== 打开模板模态框 ==========
function openTemplateModal() {
    console.log('Opening template modal');
    const modal = document.getElementById('template-modal');
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'block';
    } else {
        console.warn('Template modal not found!');
    }
}

// ========== 关闭模板模态框 ==========
function closeTemplateModal() {
    console.log('Closing template modal');
    const modal = document.getElementById('template-modal');
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
}

// ========== 加载模板选择下拉框 ==========
async function loadTemplateSelect() {
    console.log('=== loadTemplateSelect START ===');
    
    try {
        // 获取下拉框元素
        const select = document.getElementById('template-select');
        console.log('Template select element:', select);
        
        if (!select) {
            console.error('❌ Template select element NOT found!');
            return;
        }
        
        console.log('Fetching templates from API...');
        const data = await api.listTemplates(1, 100);
        
        console.log('API Response received:');
        console.log('  - page:', data.page);
        console.log('  - per_page:', data.per_page);
        console.log('  - total:', data.total);
        console.log('  - templates:', data.templates);
        console.log('  - templates length:', data.templates ? data.templates.length : 'N/A');
        
        // 清空现有选项（除了第一个）
        console.log('Clearing existing options...');
        while (select.options.length > 1) {
            select.remove(1);
        }
        console.log('Options cleared. Current count:', select.options.length);
        
        // 检查模板数据
        if (!data.templates) {
            console.warn('⚠️ data.templates is undefined');
            return;
        }
        
        if (data.templates.length === 0) {
            console.warn('⚠️ No templates found');
            const option = document.createElement('option');
            option.value = '';
            option.textContent = '暂无模板';
            option.disabled = true;
            select.appendChild(option);
            return;
        }
        
        // 添加模板选项
        console.log('Adding', data.templates.length, 'template options...');
        
        data.templates.forEach((template, index) => {
            console.log(`  [${index}] Adding template:`, {
                id: template.id,
                name: template.name
            });
            
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            
            console.log('    Option created:', {
                value: option.value,
                text: option.textContent
            });
            
            select.appendChild(option);
            
            console.log('    Option added. Total options now:', select.options.length);
        });
        
        console.log('✅ Template select loaded successfully');
        console.log('Final options count:', select.options.length);
        console.log('=== loadTemplateSelect END ===');
        
    } catch (error) {
        console.error('❌ Failed to load templates');
        console.error('Error:', error);
        console.error('Error message:', error.message);
        
        const select = document.getElementById('template-select');
        if (select) {
            select.innerHTML = '<option value="">加载失败，请重试</option>';
        }
        
        showNotification('❌ 加载模板失败：' + (error.message || '未知错误'), 'error');
    }
}

// ========== 加载模板预览 ==========
async function loadTemplatePreview(templateId) {
    console.log('=== loadTemplatePreview START, templateId:', templateId, '===');
    
    try {
        console.log('Fetching template details...');
        const template = await api.getTemplate(templateId);
        console.log('Template loaded:', template);
        
        // 更新预览
        const preview = document.getElementById('template-preview');
        if (!preview) {
            console.error('Preview element not found!');
            return;
        }
        
        console.log('Updating preview...');
        preview.innerHTML = `
            <div class="preview-subject">
                <strong>📌 邮件主题:</strong><br>
                ${escapeHtml(template.subject)}
            </div>
            <div class="preview-content">
                <strong>📝 邮件内容:</strong><br>
                ${escapeHtml(template.content).replace(/\n/g, '<br>')}
            </div>
        `;
        
        console.log('Preview updated');
        console.log('Template variables:', template.variables);
        
        // 生成变量输入框
        const variablesContainer = document.getElementById('template-variables');
        if (!variablesContainer) {
            console.error('Variables container not found!');
            return;
        }
        
        // 只在有变量时才显示
        if (template.variables && template.variables.length > 0) {
            console.log('Creating variable inputs for:', template.variables);
            variablesContainer.innerHTML = `
                <div class="variables-header">
                    <h4>⚙️ 模板变量</h4>
                    <p class="variables-hint">请为以下模板变量填写具体的值，邮件发送时会自动替换</p>
                </div>
            `;
            
            template.variables.forEach((varName, index) => {
                console.log('Creating input for variable:', varName);
                const div = document.createElement('div');
                div.className = 'form-group';
                div.innerHTML = `
                    <label for="var-${index}">
                        <span class="var-name">${varName}</span>
                        <span class="required">*</span>
                    </label>
                    <input 
                        type="text" 
                        id="var-${index}"
                        data-variable="${varName}" 
                        placeholder="输入 ${varName} 的值"
                        required
                    >
                `;
                variablesContainer.appendChild(div);
            });
            
            console.log('Variable inputs created');
        } else {
            console.log('No variables in template');
            variablesContainer.innerHTML = `
                <div class="no-variables">
                    <p>✅ 此模板无需填写变量，可直接发送</p>
                </div>
            `;
        }
        
        console.log('✅ Template preview loaded');
        console.log('=== loadTemplatePreview END ===');
        
    } catch (error) {
        console.error('❌ Failed to load template preview');
        console.error('Error:', error);
        showNotification('❌ 加载模板失败：' + (error.message || '未知错误'), 'error');
    }
}