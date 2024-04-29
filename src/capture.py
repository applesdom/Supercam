import logging
import os
import threading

from device import *

# Each Capture manages a single child ffmpeg process
# Set params, then call start(), 
class Capture:
    # Status constants
    INITIALIZED = 0
    RUNNING     = 1
    STOPPED     = 2
    FAULTED     = 3

    def __init__(self):
        self.child = None
        self.status = Capture.INITIALIZED

        # Params (no effect after .start() is called)
        self.video_device = None
        self.video_format = 'mjpeg'
        self.video_size = '640x480'
        self.video_framerate = '60'
        self.video_bitrate = '1800k'
        self.video_overlay = True
        self.video_overlay_template = '%{localtime\:%a, %b %e, %Y %-I\\\\\:%M\\\\\:%S %p}'
        self.output_dir = './cam1'
        self.output_template = 'cam1_%Y-%m-%d_%H-%M-%S.mp4'
        self.output_segment_length = '3600'

    # Don't call directly, use start()
    def __run(self):
        # Create output dir, if needed
        output_dir_absolute = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.output_dir)
        if not os.path.exists(self.output_dir):
            logging.info('Creating output directory: %s' % (self.output_dir))
            os.makedirs(self.output_dir, exist_ok=True)
            # TODO: Check for error

        # Build ffmpeg command
        cmd = ['ffmpeg', '-y', '-hide_banner']
        cmd += ['-f', 'v4l2', '-input_format', self.video_format, '-s', self.video_size, '-i', self.video_device]
        #cmd += ['-vf', 'drawtext=\"fontfile=FreeSans.ttf:fontsize=12:fontcolor=white:x=2:y=2:shadowcolor=black:shadowx=1:shadowy=1:text=\'' + self.video_overlay_template + '\'\"',]
        #cmd += ['-pix_fmt', 'yuv420p', '-b:v', self.video_bitrate]
        cmd += ['-f', 'segment', '-segment_time', self.output_segment_length, '-segment_atclocktime', '1', '-reset_timestamps', '1', '-strftime', '1', self.output_dir + self.output_template]

        # Print full command for debugging purposes
        logging.debug('Executing command:')
        logging.debug(' '.join(cmd))
    
        # Execute ffmpeg command
        self.child = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.status = Capture.RUNNING
        logging.info('Started ffmpeg child process (pid=%d)' % (self.child.pid))

        # Monitor ffmpeg child process
        while True:
            line = self.child.stdout.readline()
            if len(line) == 0:
                break

            for subline in line[:-1].decode('utf-8').split('\r'):
                logging.debug('[ffmpeg] ' + subline)

        self.status = Capture.STOPPED
        logging.info('ffmpeg child process (pid=%d) has ended' % (self.child.pid))

    # Execute __run() in a new thread, then return
    def start(self):
        threading.Thread(target=self.__run,).start()

    def stop(self):
        self.child.kill()
