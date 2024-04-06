import subprocess

class Device:
    def __init__(self):
        self.name = 'lol'

def poll_devices():
    result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE)
    devices = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if len(line) > 0 and not line.startswith('\t'):
            devices.append(line[0:line.index(' (')])
    return devices