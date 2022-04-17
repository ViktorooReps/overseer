from collections import defaultdict
from pwd import getpwall
from time import sleep
from typing import Callable, NamedTuple, Tuple

from nvitop import Device, GpuProcess


class GPUStatus(NamedTuple):
    total_memory: int
    occupied_memory: Tuple[int, ...]
    occupied_by: Tuple[str, ...]


def _collect_process_info(process: GpuProcess) -> Tuple[str, int]:
    return process.username(), process.gpu_memory()


def _collect_gpu_status() -> Tuple[GPUStatus, ...]:
    devices = Device.all()

    def to_mb(_bytes: int) -> int:
        return _bytes // 1024 // 1024

    gpu_statuses = []
    for device_idx, device in enumerate(devices):
        users_memory_consumption = defaultdict(int)
        for username, memory in map(_collect_process_info, device.processes().values()):
            users_memory_consumption[username] += memory

        total_memory = to_mb(device.memory_total())
        occupied_memory = []
        occupied_by = []
        for username, total_memory_consumed in users_memory_consumption.items():
            occupied_by.append(username)
            occupied_memory.append(to_mb(total_memory_consumed))

        gpu_statuses.append(GPUStatus(total_memory=total_memory, occupied_memory=tuple(occupied_memory), occupied_by=tuple(occupied_by)))

    return tuple(gpu_statuses)


def _status_considerably_changed(previous_status: Tuple[GPUStatus, ...], current_status: Tuple[GPUStatus, ...]) -> bool:
    previous_total_memory = tuple(gpu_status.total_memory for gpu_status in previous_status)
    current_total_memory = tuple(gpu_status.total_memory for gpu_status in current_status)

    previous_users = tuple(tuple(sorted(gpu_status.occupied_by)) for gpu_status in previous_status)
    current_users = tuple(tuple(sorted(gpu_status.occupied_by)) for gpu_status in current_status)

    def relative_memory_change(previous_gpu_status: GPUStatus, current_gpu_status: GPUStatus) -> float:
        return (sum(current_gpu_status.occupied_memory) - sum(previous_gpu_status.occupied_memory)) / previous_gpu_status.total_memory

    memory_usage_change = tuple(relative_memory_change(p_gpu, c_gpu) for p_gpu, c_gpu in zip(previous_status, current_status))
    considerable_memory_usage_change = any(abs(change) > 0.5 for change in memory_usage_change)

    return considerable_memory_usage_change or current_total_memory != previous_total_memory or current_users != previous_users


def _collect_message(status: Tuple[GPUStatus, ...]) -> str:
    username_descriptions = {pw.pw_name: pw.pw_gecos for pw in getpwall()}

    msg = 'Status changed!'
    for gpu_idx, gpu_status in enumerate(status):
        utilization = (sum(gpu_status.occupied_memory) / gpu_status.total_memory) * 100
        msg += f'\n\n<b>GPU{gpu_idx}</b> <code>{sum(gpu_status.occupied_memory)}/{gpu_status.total_memory}</code> Mb ({utilization:.2f}%):'
        if not len(gpu_status.occupied_by):
            msg += '\n    vacant!'
        for username, memory in zip(gpu_status.occupied_by, gpu_status.occupied_memory):
            description = username_descriptions[username].replace(',,,', '')
            if len(description):
                msg += f'\n    {username} ({description}), <code>{memory}</code> Mb'
            else:
                msg += f'\n    {username}, <code>{memory}</code> Mb'

    return msg


def run_monitoring(logger: Callable[[str], None], interval: int = 1) -> None:
    previous_status = tuple()
    while True:
        try:
            current_status = _collect_gpu_status()
            if _status_considerably_changed(previous_status, current_status):
                msg = _collect_message(current_status)
                logger(msg)
                previous_status = current_status
        except Exception:
            pass

        sleep(interval)
