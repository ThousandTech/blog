import psutil
import platform
import time
import json
from uptime import uptime
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .models import TerminalMonitor
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def _get_cpu_name():
    # Try platform first, then /proc/cpuinfo on Linux, fallback
    name = platform.processor()
    if name:
        return name
    try:
        with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
            for line in f:
                if 'model name' in line:
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return 'Unknown CPU'


def _format_uptime(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return ' '.join(parts)


def system_info(request):
    """API endpoint that returns static system information as JSON.
    This should be called once and cached client-side.
    """
    try:
        sys = platform.uname()
        up = uptime()
        data = {
            'system_info': f"{sys.system.lower()} {sys.machine} {sys.release}",
            'node': sys.node,
            'processor': sys.processor,
            'kernel_version': sys.release,
            'cpu_name': _get_cpu_name(),
            'uptime_seconds': int(up),
            'uptime': _format_uptime(up),
        }
    except Exception as e:
        data = {
            'error': str(e),
            'system_info': 'unknown',
            'node': 'unknown',
            'processor': 'unknown',
            'kernel_version': 'unknown',
            'cpu_name': 'unknown',
            'uptime_seconds': 0,
            'uptime': 'unknown',
        }
    return JsonResponse(data)


def system_state_details(request):
    cpu = psutil.cpu_times_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    data = {
        'cpu': {
            'count': psutil.cpu_count(),
            'user': cpu.user,
            'system': cpu.system,
        },
        'mem': {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used,
        },
        'disk': list(disk),
        'net': list(net),
        'time': time.time(),
    }
    return JsonResponse(data)

@csrf_exempt
def terminal_status_receive(request):
    if request.method == 'POST':
        terminal_status = json.loads(request.body)
        if terminal_status['imei'] in settings.ALLOWED_IMEIS:
            TerminalMonitor.objects.create(
                imei = terminal_status['imei'],
                percent = terminal_status['percent'],
                is_charging = (str(terminal_status['charging'])=='1'),
                busy_time = terminal_status['busy'],
                up_time = terminal_status.get('uptime', 0)
            )

            return HttpResponse('ok')
        else:
            return HttpResponse('不接受此终端的上报,请联系管理员')
    else:
        return HttpResponse('终端状态上报仅允许POST请求')

from django.utils import timezone

def terminal_status_latest(request):
    latest_status = TerminalMonitor.objects.order_by('-created').first()
    if latest_status:
        # 转换为本地时间
        created_local = timezone.localtime(latest_status.created)
        
        # 计算是否超时（例如5分钟无上报视为离线）
        time_diff = (timezone.now() - latest_status.created).total_seconds()
        is_offline = time_diff > 300  # 300秒 = 5分钟
        
        data = {
            'percent': latest_status.percent,
            'is_charging': latest_status.is_charging,
            'busy_time': latest_status.busy_time,
            'up_time': latest_status.up_time,
            'created': created_local.strftime('%Y-%m-%d %H:%M:%S'),
            'is_offline': is_offline,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No data'}, status=404)
