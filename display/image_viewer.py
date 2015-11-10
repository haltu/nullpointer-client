'''
A control class for the video player.
'''

import sh
import logging
from media import Media


class ImageViewer(object):

    def __init__(self):
        logging.debug('Initializing ImageViewer')
        self.process = None

    def display_content(self, content):
        assert content.content_type == Media.IMAGE
        logging.debug('ImageViewer receiving content %s', content)
        uri = content.content_uri
        self.process = sh.fbi('--noverbose', uri)#, _bg=True)

    # Cannot really hide player, must shut down
    def hide(self):
        logging.debug('ImageViewer hide called')
        self.shutdown()

    def shutdown(self):
        logging.debug('ImageViewer shutdown called')
        if self.is_alive():
            self.process.kill()
            '''
        # The video player creates 2 processes to be killed
        def kill(pgrep_line):
            pid = str(pgrep_line).strip()
            if str(pid).isdigit():
                logging.debug('Killing ImageViewer PID %s', str(pid))
                sh.kill(-9, str(pid))
        if self.is_alive():
            # Finds PIDs of fbi and passes them to the kill func
            sh.pgrep('fbi', _out=kill)
'''
    def is_alive(self):
        if self.process is None:
            return False
        else:
            return self.process.process.exit_code is None
