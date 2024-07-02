#!/bin/python3

import logging
import os
import signal
import subprocess
import sys
import time

from capture import *
from device import *
from log import *

def run():
    # Set up logging (for daemon process)
    set_up_logging()

    # Grab lockfile
    pid = os.getpid()
    with open('.supercam.lock', 'w') as f:
        f.write(str(pid) + '\n')

    # Set up sigint handler for graceful shutdown
    def handle(signum, frame):
        logging.debug('Captured signal: %d' % signum)
        if signum == signal.SIGINT:
            os.remove('.supercam.lock')
            logging.debug('Deleted lockfile')
            logging.info('Supercam has left the building.')
            sys.exit()
    signal.signal(signal.SIGINT, handle)

    # Main loop
    logging.info('Supercam has begun.')
    # logging.info('I am supercam.')
    # logging.info('I\'m your favorite camera software\'s favorite camera software.')

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
    
    # Cleanup
    os.remove('.supercam.lock')
    logging.debug('Deleted lockfile')
    logging.info('Supercam has left the building.')
    sys.exit()


### Client code starts here ###

ACTION_DEFAULT = 0
ACTION_START = 1
ACTION_STOP = 2
ACTION_RESTART = 3
ACTION_CHECK_STATUS = 4

def main():
    # Set up logging (for client process)
    client_formatter = logging.Formatter(fmt='[%(asctime)s] [%(process)d] [Client] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', style='%')
    file_handler = logging.FileHandler('supercam.log', encoding='utf-8')
    file_handler.setFormatter(client_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) 
    logger.addHandler(file_handler)

    # First log statement goes to file only, not terminal
    logging.info(' '.join(sys.argv))

    # Finish setting up logging (for client process)
    print_handler = logging.StreamHandler()
    print_handler.setFormatter(client_formatter)
    logger.addHandler(print_handler)

    # Parse action from command line args
    if len(sys.argv) < 2:
        action = ACTION_DEFAULT
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            action = ACTION_START
        elif sys.argv[1] == 'stop':
            action = ACTION_STOP
        elif sys.argv[1] == 'restart':
            action = ACTION_RESTART
        elif sys.argv[1] == 'status':
            action = ACTION_CHECK_STATUS
        else:
            logging.info('Unknown action: ' + sys.argv[1])
            # TODO: Print usage message
            return
    else:
        logging.info('Too many arguments')
        # TODO: Print usage message
        return

    # Check if supercam is already running (via lockfile)
    try:
        with open('.supercam.lock', 'r') as f:
            pid = int(f.readline())
        logging.debug('Read pid=%d from lockfile' % pid)
        # Confirm pid is still active
        pid_active = False
        result = subprocess.check_output(['ps', '-ef'])
        result = result.decode('utf-8')
        for line in result.split('\n'):
            if str(pid) in line and 'supercam' in line:
                logging.debug('Confirmed active process: ' + line)
                pid_active = True
                break
        if not pid_active:
            logging.warn('Supercam (pid=%d) did not shut down correctly. There may be orphan processes!' % pid)
            pid = None
    except FileNotFoundError:
        logging.debug('Lockfile not found')
        pid = None

    # Perform stop action
    if action == ACTION_STOP or action == ACTION_RESTART:
        if pid is None:
            logging.info('Supercam is already stopped')
        else:
            logging.info('Stopping supercam (pid=%d)...' % pid)
            os.kill(pid, signal.SIGINT)
            # Wait a maximum 10 seconds to confirm shutdown
            for n in range(20):
                time.sleep(0.5)
                logging.debug('Checking lockfile...')
                if not os.path.isfile('.supercam.lock'):
                    logging.debug('Lockfile gone')
                    logging.info('Supercam has stopped')
                    pid = None
                    break
            if pid:
                logging.error('Supercam could not be stopped!')
                return
            
    # Perform status action
    if (action == ACTION_DEFAULT and pid) or action == ACTION_CHECK_STATUS:
        # TODO: Retrieve more detailed running status
        if pid:
            logging.info('Supercam is running (pid=%d)' % pid)
        else:
            logging.info('Supercam is stopped')
        return

    # Perform start action
    if (action == ACTION_DEFAULT and pid is None) or action == ACTION_START or action == ACTION_RESTART:
        if pid:
            logging.info('Supercam is already running')
        else:
            # Start daemon
            logging.info('Starting supercam...')
            if os.fork() > 0:
                # This is the parent process (client)
                # Wait a maximum 10 seconds to confirm startup
                pid = None
                for n in range(20):
                    time.sleep(0.5)
                    logging.debug('Checking lockfile...')
                    try:
                        with open('.supercam.lock', 'r') as f:
                            pid = int(f.readline())
                            logging.debug('Lockfile created')
                            logging.info('Supercam is running (pid=%d)' % pid)
                            break
                    except FileNotFoundError:
                        pass
                if pid is None:
                    logging.error('Supercam could not be started!')
            else:
                # This is the child process (intermediary)
                os.setsid()
                if os.fork() > 0:
                    # This is the 2nd parent process (intermediary)
                    sys.exit()
                else:
                    # This is the 2nd child process (daemon)
                    run()

if __name__ == '__main__':
    main()
