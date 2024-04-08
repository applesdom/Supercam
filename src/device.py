import subprocess

class VideoDevice:
    def __init__(self, name, handle):
        self.name = name
        self.handle = handle

    def __str__(self):
        return '%s (%s)' % (self.name, self.handle)

def poll_video_devices():
    # Run command to get list of devices
    result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE)

    # Parse names and handles
    # TODO: Handle no-devices-connected case
    result_string = result.stdout.decode('utf-8')
    devices = []
    name = None
    for line in result_string.split('\n'):
        if len(line) == 0:
            continue
        elif not line.startswith('\t'):
            name = line[0:line.index(' (')]
        elif name != None:
            handle = line[1:]
            devices.append(VideoDevice(name, handle))
            name = None

    return devices