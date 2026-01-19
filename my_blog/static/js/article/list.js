document.addEventListener('DOMContentLoaded', function () {
    var configEl = document.getElementById('monitor-config');
    var terminalUrl = configEl ? configEl.dataset.monitorTerminalUrl : null;

    function updateLiveTime() {
        var birthTime = new Date(2004, 8, 18, 15, 30, 0);
        var now = new Date();

        var years = now.getFullYear() - birthTime.getFullYear();
        var months = now.getMonth() - birthTime.getMonth();
        var days = now.getDate() - birthTime.getDate();
        var hours = now.getHours() - birthTime.getHours();
        var minutes = now.getMinutes() - birthTime.getMinutes();
        var seconds = now.getSeconds() - birthTime.getSeconds();

        if (seconds < 0) {
            seconds += 60;
            minutes--;
        }
        if (minutes < 0) {
            minutes += 60;
            hours--;
        }
        if (hours < 0) {
            hours += 24;
            days--;
        }
        if (days < 0) {
            var lastMonth = new Date(now.getFullYear(), now.getMonth(), 0);
            days += lastMonth.getDate();
            months--;
        }
        if (months < 0) {
            months += 12;
            years--;
        }

        var timeStr = years + 'y ' + months + 'm ' + days + 'd ' + hours + 'h ' + minutes + 'm ' + seconds + 's';
        var liveTimeEl = document.getElementById('live-time');
        if (liveTimeEl) {
            liveTimeEl.textContent = timeStr;
        }
    }

    updateLiveTime();
    setInterval(updateLiveTime, 1000);

    var terminalUpTime = null;
    var isTerminalOffline = false;

    function formatUptime(seconds) {
        if (seconds === null || seconds === undefined) return '-';
        var days = Math.floor(seconds / (3600 * 24));
        var hours = Math.floor((seconds % (3600 * 24)) / 3600);
        var minutes = Math.floor((seconds % 3600) / 60);
        var secs = Math.floor(seconds % 60);

        var result = '';
        if (days > 0) result += days + 'd ';
        if (hours > 0) result += hours + 'h ';
        result += minutes + 'm ';
        result += secs + 's';
        return result;
    }

    function tickTerminalTime() {
        if (terminalUpTime !== null && !isTerminalOffline) {
            terminalUpTime++;
            var el = document.getElementById('terminal-uptime');
            if (el) {
                el.textContent = formatUptime(terminalUpTime);
            }
        }
    }
    setInterval(tickTerminalTime, 1000);

    function updateTerminalStatus() {
        if (!terminalUrl) {
            return;
        }
        fetch(terminalUrl)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function (data) {
                var contentDiv = document.getElementById('terminal-status-content');
                if (!contentDiv) {
                    return;
                }
                if (data.error) {
                    contentDiv.innerHTML = '<p class="text-muted small">暂无数据</p>';
                    return;
                }

                terminalUpTime = data.up_time;
                isTerminalOffline = data.is_offline;

                var statusText = data.is_charging ? '充电中' : '在线';
                var statusColor = data.is_charging ? 'var(--success)' : 'var(--accent)';
                var timeDisplay = data.created;

                if (data.is_offline) {
                    statusText = '离线';
                    statusColor = 'var(--muted)';
                }

                var adminState = '空闲或摆烂';
                var adminColor = 'var(--success)';

                if (data.busy_time > 900) {
                    adminState = '忙碌或昏迷';
                    adminColor = 'var(--accent)';
                }

                if (data.is_offline) {
                    adminState = '失联';
                    adminColor = 'var(--muted)';
                }

                var adminStateEl = document.getElementById('admin-state-text');
                if (adminStateEl) {
                    adminStateEl.textContent = adminState;
                    adminStateEl.style.color = adminColor;
                }

                function getBatteryColor(percent) {
                    var startR = 255, startG = 107, startB = 107;
                    var endR = 159, endG = 232, endB = 112;
                    var ratio = percent / 100;
                    var r = Math.round(startR + (endR - startR) * ratio);
                    var g = Math.round(startG + (endG - startG) * ratio);
                    var b = Math.round(startB + (endB - startB) * ratio);
                    return 'rgb(' + r + ', ' + g + ', ' + b + ')';
                }

                var batteryColor = getBatteryColor(data.percent);
                var batteryText = data.percent + '%';
                var batteryWidth = data.percent;

                if (data.is_offline) {
                    batteryColor = 'var(--muted)';
                    batteryText = 'NaN';
                    batteryWidth = 0;
                }

                contentDiv.innerHTML = '\
                    <div class="d-flex justify-content-between mb-2">\
                        <span>电量</span>\
                        <span style="color: ' + batteryColor + '; font-weight: bold;">' + batteryText + '</span>\
                    </div>\
                    <div class="progress mb-3" style="height: 6px; background-color: rgba(127, 127, 127, 0.3);">\
                        <div class="progress-bar" role="progressbar" \
                             style="width: ' + batteryWidth + '%; background-color: ' + batteryColor + ';" \
                             aria-valuenow="' + batteryWidth + '" aria-valuemin="0" aria-valuemax="100"></div>\
                    </div>\
                    <div class="d-flex justify-content-between mb-0">\
                        <span>状态</span>\
                    </div>\
                    <div class="mt-1 mb-2">\
                        <span class="text-muted small" style="font-size: 0.85rem; color: ' + statusColor + ' !important;">' + statusText + '</span>\
                    </div>\
                    <div class="d-flex justify-content-between mb-0">\
                        <span>运行时长</span>\
                    </div>\
                    <div class="mt-1 mb-2">\
                        <span id="terminal-uptime" class="text-muted small" style="font-size: 0.85rem; color: #9aa3b0 !important;">' + formatUptime(data.up_time) + '</span>\
                    </div>\
                    <div class="d-flex justify-content-between mb-0">\
                        <span>' + (data.is_offline ? '最后上报时间' : '更新时间') + '</span>\
                    </div>\
                    <div class="mt-1">\
                        <span class="text-muted small" style="font-size: 0.85rem; color: #9aa3b0 !important;">' + timeDisplay + ' (UTC+8)</span>\
                    </div>\
                ';
            })
            .catch(function () {});
    }

    updateTerminalStatus();
    setInterval(updateTerminalStatus, 60000);
});

document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.mobile-tab-item');
    const mainFeed = document.querySelector('.main-feed');
    const sidebarLeft = document.querySelector('.sidebar-left');
    const sidebarRight = document.querySelector('.sidebar-right');
    
    // 内容区域
    const aboutContent = document.querySelectorAll('.mobile-content-about');
    const categoriesContent = document.querySelectorAll('.mobile-content-categories');
    
    // 仅在移动端生效的 Tab 切换逻辑
    function switchTab(tabName) {
        // 1. 更新 Tab 状态
        tabs.forEach(t => {
            if (t.dataset.tab === tabName) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        // 2. 如果是桌面端，不做任何内容隐藏操作（依靠 CSS 媒体查询）
        if (window.innerWidth >= 992) return;

        // 3. 移动端内容显示逻辑
        // 重置所有可见性
        mainFeed.style.display = 'none';
        sidebarLeft.style.display = 'none';
        sidebarRight.style.display = 'none';
        
        // 隐藏 Sidebar Left 内部的所有子模块
        aboutContent.forEach(el => el.style.display = 'none');
        categoriesContent.forEach(el => el.style.display = 'none');
        
        // 根据 Tab 显示对应内容
        if (tabName === 'articles') {
            mainFeed.style.display = 'block';
        } else if (tabName === 'categories') {
            sidebarLeft.style.display = 'block';
            categoriesContent.forEach(el => el.style.display = 'block');
        } else if (tabName === 'about') {
            sidebarLeft.style.display = 'block';
            sidebarRight.style.display = 'block';
            aboutContent.forEach(el => el.style.display = 'block');
            // 切换到关于页面时，强制刷新图表大小
            if (window.monitorDiskChart) window.monitorDiskChart.resize();
            if (window.monitorNetChart) window.monitorNetChart.resize();
        }
    }

    // 绑定点击事件
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    // 初始化：默认显示文章
    if (window.innerWidth < 992) {
        switchTab('articles');
    }

    // 监听窗口大小变化，恢复/重置显示
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 992) {
            // 桌面端恢复所有元素的显示
            mainFeed.style.display = '';
            sidebarLeft.style.display = '';
            sidebarRight.style.display = '';
            aboutContent.forEach(el => el.style.display = '');
            categoriesContent.forEach(el => el.style.display = '');
        } else {
            // 切回移动端时，重新应用当前激活的 Tab
            const activeTab = document.querySelector('.mobile-tab-item.active');
            if (activeTab) {
                switchTab(activeTab.dataset.tab);
            }
        }
    });
});
