(function () {
    var configEl = document.getElementById('monitor-config');
    if (!configEl) {
        return;
    }
    var infoUrl = configEl.dataset.monitorInfoUrl;
    var stateUrl = configEl.dataset.monitorStateUrl;

    var uptimeBaseSeconds = null;
    var uptimeSyncTime = null;

    function formatUptimeSeconds(totalSeconds) {
        totalSeconds = Math.floor(totalSeconds);
        var days = Math.floor(totalSeconds / 86400);
        totalSeconds = totalSeconds % 86400;
        var hours = Math.floor(totalSeconds / 3600);
        totalSeconds = totalSeconds % 3600;
        var minutes = Math.floor(totalSeconds / 60);
        var seconds = totalSeconds % 60;
        var parts = [];
        if (days) parts.push(days + 'd');
        if (hours) parts.push(hours + 'h');
        if (minutes) parts.push(minutes + 'm');
        parts.push(seconds + 's');
        return parts.join(' ');
    }

    function renderUptimeFromBase() {
        if (uptimeBaseSeconds === null || uptimeSyncTime === null) return;
        var nowSec = Date.now() / 1000;
        var elapsed = nowSec - uptimeSyncTime;
        if (elapsed < 0) elapsed = 0;
        var total = uptimeBaseSeconds + elapsed;
        var upEl = document.getElementById('uptime');
        if (upEl) upEl.innerText = formatUptimeSeconds(total);
    }

    function usageColor(pct) {
        var v = Math.max(0, Math.min(100, pct));
        var hue = 120 - v * 1.2;
        if (hue < 0) hue = 0;
        return 'hsl(' + hue + ', 70%, 45%)';
    }

    function updateStaticInfo(data) {
        if (data.system_info) {
            var sysEl = document.getElementById('system-version');
            if (sysEl) sysEl.innerText = data.system_info;
        }
        if (data.node) {
            var hostEl = document.getElementById('hostname');
            if (hostEl) hostEl.innerText = data.node;
        }
        if (data.cpu_name) {
            var cpuNameEl = document.getElementById('cpu-name');
            if (cpuNameEl) cpuNameEl.innerText = data.cpu_name;
        }
        if (typeof data.uptime_seconds === 'number') {
            uptimeBaseSeconds = data.uptime_seconds;
            uptimeSyncTime = Date.now() / 1000;
            renderUptimeFromBase();
        }
    }

    function updateFromData(data) {
        var cpu = data.cpu;
        var cpuUsed = cpu.user + cpu.system;
        if (cpuUsed < 0) cpuUsed = 0;
        if (cpuUsed > 100) cpuUsed = 100;

        var cpuBar = document.getElementById('cpu-bar');
        var cpuText = document.getElementById('cpu-percent-text');
        if (cpuBar && cpuText) {
            cpuBar.style.width = cpuUsed.toFixed(1) + '%';
            cpuBar.style.backgroundColor = usageColor(cpuUsed);
            cpuText.innerText = cpuUsed.toFixed(1) + '%';
        }

        var mem = data.mem;
        var memBar = document.getElementById('mem-bar');
        var memPercentText = document.getElementById('mem-percent-text');
        var memUsageText = document.getElementById('mem-usage-text');
        if (memBar && memPercentText && memUsageText) {
            memBar.style.width = mem.percent.toFixed(1) + '%';
            memBar.style.backgroundColor = usageColor(mem.percent);
            memPercentText.innerText = mem.percent.toFixed(1) + '%';
            var usedGB = mem.used / (1024 * 1024 * 1024);
            var totalGB = mem.total / (1024 * 1024 * 1024);
            memUsageText.innerText = usedGB.toFixed(1) + 'G/' + totalGB.toFixed(1) + 'G';
        }

        if (window.monitorDiskChart && window.monitorNetChart) {
            disk.load(window.monitorDiskChart, data.disk.slice(2, 4), data.time, ['Read', 'Write'], 'I/O');
            net.load(window.monitorNetChart, data.net, data.time, ['Out', 'In'], 'Traffic');
        }
    }

    function initEcharts(id) {
        var dom = document.getElementById(id);
        if (!dom || typeof echarts === 'undefined') return null;
        var myChart = echarts.init(dom);
        return myChart;
    }

    function timeSeriesData() {
        var obj = {};
        obj.load = function (chart, data, time, legend, label) {
            var speed = [0, 0];
            var tmp = this.tmp;
            var writeBytes = data[1];
            var readBytes = data[0];
            this.tmp = {
                count: [writeBytes, readBytes],
                time: time
            };
            if (tmp != null) {
                speed = [
                    (writeBytes - tmp.count[0]) / (time - tmp.time),
                    (readBytes - tmp.count[1]) / (time - tmp.time)
                ];
            }
            this.stamp.x.push(time);
            this.stamp.y.push(speed);
            if (this.stamp.x.length >= 10) {
                this.stamp.x = this.stamp.x.slice(-10);
                this.stamp.y = this.stamp.y.slice(-10);
            }
            loadEcharts(chart, this.stamp, legend, label);
        };
        obj.tmp = null;
        obj.stamp = { x: [], y: [] };
        return obj;
    }

    function autoFormatSpeed(val) {
        if (val === null || val === undefined || isNaN(val)) return '--';
        if (val < 1024 * 1024) {
            return Math.round(val / 1024) + 'K';
        } else if (val < 1024 * 1024 * 1024) {
            return Math.round(val / (1024 * 1024)) + 'M';
        } else {
            return Math.round(val / (1024 * 1024 * 1024)) + 'G';
        }
    }

    function updateIndicators(rawPair, yLabel) {
        if (!rawPair || rawPair.length < 2) return;
        var val1 = rawPair[1];
        var val0 = rawPair[0];

        if (yLabel === 'Traffic') {
            var upEl = document.getElementById('net-up-indicator');
            var downEl = document.getElementById('net-down-indicator');
            if (upEl && downEl) {
                upEl.innerText = '↑ ' + autoFormatSpeed(val1);
                downEl.innerText = '↓ ' + autoFormatSpeed(val0);
            }
        } else if (yLabel === 'I/O') {
            var rEl = document.getElementById('disk-r-indicator');
            var wEl = document.getElementById('disk-w-indicator');
            if (rEl && wEl) {
                rEl.innerText = '↑ ' + autoFormatSpeed(val1);
                wEl.innerText = '↓ ' + autoFormatSpeed(val0);
            }
        }
    }

    function loadEcharts(chart, data, legend, yLabel) {
        var lastRawPair = null;
        if (data.y && data.y.length > 0) {
            lastRawPair = data.y[data.y.length - 1];
        }
        updateIndicators(lastRawPair, yLabel);

        var result = indexValue(data.y);
        var unit = result[0];
        var yAxis = result[1];

        var axisName = yLabel;
        if (yLabel === 'Traffic' || yLabel === 'I/O') axisName = '';

        var option = {
            backgroundColor: 'transparent',
            grid: {
                left: 45,
                right: 30,
                top: 30,
                bottom: 20,
                containLabel: false
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                formatter: function (params) {
                    var html = params[0].name + '<br>';
                    for (var i = 0; i < params.length; i++) {
                        html += params[i].marker + params[i].seriesName + ': ' + params[i].value + unit + '<br>';
                    }
                    return html;
                }
            },
            legend: {
                data: legend,
                top: 0,
                left: 0,
                textStyle: { color: '#9aa3b0', fontSize: 10 }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: data.x.map(function (a) { return timestampToTime(a); }),
                axisLabel: {
                    show: true,
                    color: '#9aa3b0',
                    fontSize: 10
                },
                axisLine: { lineStyle: { color: '#3d4a5d' } }
            },
            yAxis: {
                type: 'value',
                scale: true,
                minInterval: 1,
                splitLine: { lineStyle: { color: '#252c35' } },
                axisLabel: {
                    color: '#9aa3b0',
                    fontSize: 10,
                    formatter: function (value) {
                        return Math.round(value) + unit;
                    }
                },
                name: axisName
            },
            series: [
                {
                    name: legend[0],
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    areaStyle: { opacity: 0.1 },
                    data: yAxis.map(function (a) { return a[1].toFixed(1); }),
                    itemStyle: { color: '#c0504d' }
                },
                {
                    name: legend[1],
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    areaStyle: { opacity: 0.1 },
                    data: yAxis.map(function (a) { return a[0].toFixed(1); }),
                    itemStyle: { color: '#4f81bd' }
                }
            ]
        };
        if (chart) {
            chart.setOption(option);
        }
    }

    function timestampToTime(timestamp) {
        var date = new Date(timestamp * 1000);
        var h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
        var m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':';
        var s = (date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds());
        return h + m + s;
    }

    function indexValue(data) {
        var pool = [];
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            for (var j = 0; j < item.length; j++) {
                pool.push(item[j]);
            }
        }
        var maxValue = 0;
        if (pool.length > 0) {
            maxValue = pool.sort(function (a, b) { return b - a; })[0];
        }

        var unit = null;
        var res = [];
        if (maxValue < 1024 * 1024) {
            unit = 'K';
            res = data.map(function (i) { return [i[0] / 1024, i[1] / 1024]; });
        } else if (1024 * 1024 <= maxValue && maxValue < 1024 * 1024 * 1024) {
            unit = 'M';
            res = data.map(function (i) { return [i[0] / (1024 * 1024), i[1] / (1024 * 1024)]; });
        } else {
            unit = 'G';
            res = data.map(function (i) { return [i[0] / (1024 * 1024 * 1024), i[1] / (1024 * 1024 * 1024)]; });
        }
        return [unit, res];
    }

    var disk = timeSeriesData();
    var net = timeSeriesData();

    function fetchStaticInfo() {
        if (!infoUrl) return;
        fetch(infoUrl).then(function (res) {
            return res.json();
        }).then(function (data) {
            updateStaticInfo(data);
        }).catch(function () {});
    }

    function fetchDetails() {
        if (!stateUrl) return;
        fetch(stateUrl).then(function (res) {
            return res.json();
        }).then(function (data) {
            updateFromData(data);
        }).catch(function () {});
    }

    window.monitorDiskChart = initEcharts('disk-chart');
    window.monitorNetChart = initEcharts('network-chart');

    function updateEarthTime() {
        var now = new Date();

        var utcYear = now.getUTCFullYear();
        var utcMonth = String(now.getUTCMonth() + 1).padStart(2, '0');
        var utcDay = String(now.getUTCDate()).padStart(2, '0');
        var utcHours = String(now.getUTCHours()).padStart(2, '0');
        var utcMinutes = String(now.getUTCMinutes()).padStart(2, '0');
        var utcSeconds = String(now.getUTCSeconds()).padStart(2, '0');
        var utcStr = utcYear + '-' + utcMonth + '-' + utcDay + 'T' + utcHours + ':' + utcMinutes + ':' + utcSeconds + '+00:00';

        var utcEl = document.getElementById('utc-time');
        if (utcEl) utcEl.innerText = utcStr;

        var utcTimestamp = now.getTime() + (now.getTimezoneOffset() * 60000);
        var beijingDate = new Date(utcTimestamp + (3600000 * 8));

        var bjYear = beijingDate.getFullYear();
        var bjMonth = String(beijingDate.getMonth() + 1).padStart(2, '0');
        var bjDay = String(beijingDate.getDate()).padStart(2, '0');
        var bjHours = String(beijingDate.getHours()).padStart(2, '0');
        var bjMinutes = String(beijingDate.getMinutes()).padStart(2, '0');
        var bjSeconds = String(beijingDate.getSeconds()).padStart(2, '0');
        var bjStr = bjYear + '-' + bjMonth + '-' + bjDay + 'T' + bjHours + ':' + bjMinutes + ':' + bjSeconds + '+08:00';

        var localEl = document.getElementById('local-time');
        if (localEl) localEl.innerText = bjStr;
    }

    setInterval(fetchDetails, 2000);
    setInterval(fetchStaticInfo, 60000);
    setInterval(function () {
        renderUptimeFromBase();
        updateEarthTime();
    }, 1000);

    fetchStaticInfo();
    fetchDetails();
    updateEarthTime();
})();
