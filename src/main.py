#!/bin/python3

import logging
import time

from capture import *
from device import *
from log import *

def main():
    set_up_logging()

    logging.info('Supercam has begun.')

    device_list = poll_video_devices()
    # print('Found %d devices:')
    # for device in device_list:
    #     print('\t' + str(device))
    device = device_list[0]

    capture = Capture()
    capture.video_device = device.handle
    capture.start()

    print(capture.status)

    time.sleep(5)

    capture.stop()

if __name__ == '__main__':
    main()
