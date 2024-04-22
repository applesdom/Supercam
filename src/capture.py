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

    def start(self):
        # Create output dir, if needed
        output_dir_absolute = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.output_dir)
        if not os.path.exists(self.output_dir):
            logging.info('Creating output directory: %s' % (self.output_dir))
            os.makedirs(self.output_dir, exist_ok=True)

        # Prepare callback
        def monitor_process(process):
            logging.info('Started ffmpeg child process (pid=%d)' % (process.pid))
            line = process.stdout.readline()
            while len(line) > 0:
                for subline in line[:-1].decode('utf-8').split('\r'):
                    logging.debug(subline)
                line = process.stdout.readline()
            logging.info('ffmpeg child process (pid=%d) has ended' % (process.pid))

        video_args = ['-f', 'v4l2', '-thread_queue_size', '1024', '-input_format', self.video_format, '-s', self.video_size, '-i', self.video_device]
        if self.video_overlay:
            overlay_args = ['-vf', 'drawtext=\"fontfile=FreeSans.ttf:fontsize=12:fontcolor=white:x=2:y=2:shadowcolor=black:shadowx=1:shadowy=1:text=\'' + self.video_overlay_template + '\'\"',]
        else:
            overlay_args = []
        format_args = ['-pix_fmt', 'yuv420p', '-c:v', 'h264_v4l2m2m', '-flags', '+global_header', '-b:v', self.video_bitrate, '-y', '-hide_banner']
        output_args = ['-f', 'segment', '-segment_format_options', 'movflags=+faststart', '-segment_time', self.output_segment_length, '-segment_atclocktime', '1', '-reset_timestamps', '1', '-strftime', '1', self.output_dir + self.output_template]
        cmd = ['ffmpeg'] + video_args + overlay_args + format_args + output_args

        logging.debug('Executing command:')
        logging.debug(' '.join(cmd))
    
        self.child = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        threading.Thread(target=monitor_process, args=[self.child]).start()

    def stop(self):
        self.child.kill()
