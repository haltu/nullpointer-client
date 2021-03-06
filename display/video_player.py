import sh
import platform
from media import Media
import logging
from abstract_viewer import AbstractViewer


class VideoPlayer(AbstractViewer):
    '''
    A control class for the video player.
    '''

    NON_PI_PLATFORMS = ('Ubuntu', 'LinuxMint')

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing VideoPlayer')
        self.process = None

    def display_content(self, content):
        assert content.content_type == Media.VIDEO
        self.logger.debug('VideoPlayer receiving content %s', content)
        uri = content.content_uri
        if platform.linux_distribution()[0] in self.NON_PI_PLATFORMS:
            self.process = sh.vlc(
                '--no-osd', '-f', '--no-interact', '--repeat',
                '--mouse-hide-timeout', '--no-video-title-show',
                '--video-on-top', uri, _bg=True
            )
        else:
            self.process = sh.omxplayer(
                '--no-osd', '-b', '--loop', uri, _bg=True)

    # Cannot really hide player, must shut down
    def hide(self):
        self.logger.debug('VideoPlayer hide called')
        self.shutdown()

    def shutdown(self):
        self.logger.debug('VideoPlayer shutdown called')
        if self.is_alive():
            if platform.linux_distribution()[0] in self.NON_PI_PLATFORMS:
                sh.pkill('vlc')
            else:
                sh.killall('omxplayer.bin', _ok_code=[0, 1])

    def is_alive(self):
        if self.process is None:
            return False
        else:
            return self.process.process.exit_code is None
