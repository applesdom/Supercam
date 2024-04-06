#!/bin/python3

# Wrote this several months ago as a quick fix.
# Maybe it can serve as a mock-up?

import logging
import os
import signal
import subprocess
import sys
import threading
import time

VIDEO_DEVICE    = '/dev/video0'
VIDEO_FORMAT    = 'mjpeg'
VIDEO_SIZE      = '1920x1080'
VIDEO_FRAMERATE = ''
VIDEO_BITRATE   = '1800k'
VIDEO_OVERLAY   = '%{localtime\:%a, %b %e, %Y %-I\\\\\:%M\\\\\:%S %p}'

OUTPUT_DIR                 = './mousecam/'
OUTPUT_SEGMENT_LENGTH      = '3600'
OUTPUT_TEMPLATE            = 'cam1_%Y-%m-%d_%H-%M-%S.mp4'
OUTPUT_LIVE_DIR            = './cam1/live/'
OUTPUT_LIVE_TEMPLATE       = 'cam1_live.mpd'
OUTPUT_LIVE_INIT_TEMPLATE  = 'cam1_init-\$RepresentationID$.\$ext\$'
OUTPUT_LIVE_CHUNK_TEMPLATE = 'cam1_chunk-\$RepresentationID\$-\$Number%06d\$.\$ext\$'

STORAGE_LIMIT         = 26*1024*1024*1024  # In bytes
STORAGE_CULL_INTERVAL = 600

LOG_LEVEL      = logging.DEBUG
LOG_FILE       = './supercam.log'
LOG_FILE_LEVEL = logging.INFO

def main():
    def on_kill(signum, frame):
        if process != None:
            #process.send_signal(signal.SIGINT)
            logger.info('Received signal %d, waiting for ffmpeg to finish...' % (signum))
            process.wait()
        logger.info('Supercam out.')
        sys.exit()

    def monitor_process(process):
        logger.info('Started ffmpeg child process (pid=%d)' % (process.pid))
        line = process.stdout.readline()
        while len(line) > 0:
            for subline in line[:-1].decode('utf-8').split('\r'):
                logger.debug(subline)
            line = process.stdout.readline()
        logger.info('ffmpeg child process (pid=%d) has ended' % (process.pid))

    # Load settings
    # with open('settings.json') as f:
    #     lines = f.readlines()
    # settings_string = ''
    # for line in lines:
    #     if not line.strip().startswith('//'):
    #         settings_string += line + '\n'
    # settings = json.loads(settings_string)
    # print(settings)

    # Set up logging
    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', style='%')
    printer = logging.StreamHandler()
    printer.setLevel(LOG_LEVEL)
    printer.setFormatter(formatter)
    filer = logging.FileHandler(LOG_FILE, encoding='utf-8')
    filer.setLevel(LOG_FILE_LEVEL)
    filer.setFormatter(formatter)
    logger = logging.getLogger('supercam')
    logger.setLevel(logging.DEBUG)  
    logger.addHandler(printer)
    logger.addHandler(filer)
    logger.info('')
    logger.info('Supercam has begun.')

    # Set up signal callbacks
    signal.signal(signal.SIGINT, on_kill)
    signal.signal(signal.SIGTERM, on_kill)

    # Make sure output directories exists
    if not os.path.exists(OUTPUT_DIR):
        logger.info('Creating output directory: %s' % (OUTPUT_DIR))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # if not os.path.exists(OUTPUT_LIVE_DIR):
    #     logger.info('Creating live output directory: %s' % (OUTPUT_LIVE_DIR))
    # os.makedirs(OUTPUT_LIVE_DIR, exist_ok=True)

    # Launch ffmpeg
    # cmd = ['ffmpeg', '-f', 'v4l2', '-thread_queue_size', '1024', '-input_format', VIDEO_FORMAT, '-s', VIDEO_SIZE, '-framerate', VIDEO_FRAMERATE, '-i', VIDEO_DEVICE,
    #        '-vf', 'drawtext=\"fontfile=FreeSans.ttf:fontsize=12:fontcolor=white:x=2:y=2:shadowcolor=black:shadowx=1:shadowy=1:text=\'' + VIDEO_OVERLAY + '\'\"',
    #        '-pix_fmt', 'yuv420p', '-c:v', 'h264_v4l2m2m', '-flags', '+global_header', '-b:v', VIDEO_BITRATE, '-y', '-hide_banner',
    #        '-f', 'tee', '-map', '0:v',
    #        '[f=segment:segment_format_options=movflags=+frag_keyframe+empty_moov+default_base_moof:segment_time=' + OUTPUT_SEGMENT_LENGTH + ':segment_atclocktime=1:reset_timestamps=1:strftime=1]' + OUTPUT_DIR + OUTPUT_TEMPLATE + '| \
    #         [f=dash:seg_duration=2:streaming=1:window_size=10:use_template=1:init_seg_name=' + OUTPUT_LIVE_INIT_TEMPLATE + ':media_seg_name=' + OUTPUT_LIVE_CHUNK_TEMPLATE + ':remove_at_exit=1]' + OUTPUT_LIVE_TEMPLATE]
    cmd = ['ffmpeg', '-f', 'v4l2', '-thread_queue_size', '1024', '-input_format', VIDEO_FORMAT, '-s', VIDEO_SIZE, '-i', VIDEO_DEVICE,
           '-vf', 'drawtext=\"fontfile=FreeSans.ttf:fontsize=12:fontcolor=white:x=2:y=2:shadowcolor=black:shadowx=1:shadowy=1:text=\'' + VIDEO_OVERLAY + '\'\"',
           '-pix_fmt', 'yuv420p', '-c:v', 'h264_v4l2m2m', '-flags', '+global_header', '-b:v', VIDEO_BITRATE, '-y', '-hide_banner',
           '-f', 'segment', '-segment_format_options', 'movflags=+faststart', '-segment_time', OUTPUT_SEGMENT_LENGTH, '-segment_atclocktime', '1', '-reset_timestamps', '1', '-strftime', '1', OUTPUT_DIR + OUTPUT_TEMPLATE]
    logger.debug('Executing command:')
    logger.debug(' '.join(cmd))
    
    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Monitor ffmpeg process in new thread
    threading.Thread(target=monitor_process, args=[process]).start()

    # Perform periodic checks (escape via signal handler above)
    while True:
        inventory = []
        total_size = 0
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith('cam1_') and file.endswith('.mp4'):
                stats = os.stat(OUTPUT_DIR + file)
                inventory.append((OUTPUT_DIR + file, stats.st_size))
                total_size += stats.st_size
        inventory.sort(key=lambda pair: pair[0])

        while total_size > STORAGE_LIMIT:
            (file, size) = inventory.pop(0)
            os.remove(file)
            logger.info('Deleting file: ' + file)
            total_size -= size

        time.sleep(STORAGE_CULL_INTERVAL)

if __name__ == '__main__':
    main()
