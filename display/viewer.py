'''
A high-level class for viewing any supported media type.
Delegates viewing to the browser or video player depending on media
type. The displaying is performed in a separate thread, so shutdown()
must be called before killing the program to avoid errors upon
program termination.
'''

import time
import logging
from media import Media
from browser import Browser
from video_player import VideoPlayer
from image_viewer import ImageViewer


class Viewer(object):

    DISPLAY_TIME_GRANULARITY = 1  # seconds
#    BROWSER = Browser()
    IMAGE_VIEWER = ImageViewer()
    PLAYER = VideoPlayer()

    VIEWERS = {
        Media.IMAGE: IMAGE_VIEWER,
#        Media.WEB_PAGE: BROWSER,
        Media.VIDEO: PLAYER
    }

    def display_content(self, content):
        logging.debug('Viewer received content %s', content)
        viewer = self.VIEWERS[content.content_type]

        displayed_time = 0
        viewer.display_content(content)
        self.running = True

        while self.running and displayed_time < content.view_time:
            time.sleep(self.DISPLAY_TIME_GRANULARITY)
            displayed_time += self.DISPLAY_TIME_GRANULARITY
            self.keep_alive(viewer, content)

        viewer.hide()
        logging.debug('Viewer finished displaying content %s', content)

    def keep_alive(self, viewer, content):
        if not viewer.is_alive():
            logging.debug('Resurrecting viewer for content %s', content)
            viewer.display_content(content)

    def shutdown(self):
        logging.debug('Viewer shutdown requested')
        self.running = False
 #       self.BROWSER.shutdown()
        self.PLAYER.shutdown()
        logging.debug('Viewer shutdown complete')
