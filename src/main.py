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
    logging.info('Capture state: %d' % (capture.status))
    logging.info('Starting video capture')
    capture.start()
    logging.info('waiting for 1 second')
    time.sleep(1)
    logging.info('Capture state: %d' % (capture.status))
    logging.info('waiting for 5 seconds')
    time.sleep(5)
    logging.info('Stopping video capture')
    capture.stop()
    logging.info('Waiting for 2 seconds')
    time.sleep(2)
    logging.info('Capture state: %d' % (capture.status))

if __name__ == '__main__':
    main()
