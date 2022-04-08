from time import sleep
from typing import Callable

from nvitop import Device


def run_monitoring(logger: Callable[[str], None], interval: int = 1) -> None:
    prev_status = [None]
    while True:
        devices = Device.all()
        curr_status = [False] * len(devices)
        for device_idx, device in enumerate(devices):
            if not len(device.processes()):
                curr_status[device_idx] = True

        if tuple(curr_status) != tuple(prev_status):
            msg = f'Status changed!\n'
            for device_idx, device_status in enumerate(curr_status):
                if device_status:
                    msg += f'GPU{device_idx}: vacant!\n'
                else:
                    process = list(devices[device_idx].processes().values())[0]
                    username = process.username()
                    msg += f'GPU{device_idx}: occupied by {username}\n'
            logger(msg)

        prev_status = curr_status
        sleep(interval)
