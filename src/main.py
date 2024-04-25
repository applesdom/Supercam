#!/bin/python3

import logging
import time

from capture import *
from device import *
from log import *

def main():
    set_up_logging()
    logging.info('Supercam has begun.')

    # Device discovery test
    device_list = poll_video_devices()
    if len(device_list) == 0:
        logging.info('No devices found.')
    else:
        logging.info('Found %d devices:' % (len(device_list)))
        for device in device_list:
            logging.info('\t' + str(device))

    # 5 second video capture test
    capture = Capture()
    capture.video_device = '/dev/video0'
    logging.info('Starting video capture...')
    capture.start()
    time.sleep(5)
    capture.stop()
    logging.info('Ended video capture')

if __name__ == '__main__':
    main()
