import logging
import os
from stat import ST_ATIME
from display.media import Media

class MediaCleaner(object):
    '''
    Checks available disk space and removes unused media.
    '''
    LOG = logging.getLogger(__name__)

    def __init__(self, config, playlist_parser):
        threshold_mb = int(config.get('Storage', 'cleanup_threshold_mb'))
        self.CLEANUP_THRESHOLD_BYTES = threshold_mb * 1000 * 1000
        extra_space = int(config.get('Storage', 'cleanup_extra_space_to_free_up_mb'))
        self.EXTRA_SPACE_TO_FREE_UP_BYTES = extra_space * 1000 * 1000
        self.MEDIA_FOLDER = config.get('Storage', 'media_folder')
        self.PLAYLIST_PARSER = playlist_parser
        self.LOG.debug('Initialized %s' % __name__)

    def enough_space(self, content_length):
        statvfs = os.statvfs(self.MEDIA_FOLDER)
        free_blocks = statvfs.f_bavail
        block_size = statvfs.f_frsize
        free_bytes = free_blocks* block_size
        self.LOG.debug('Free space in bytes: %s',free_bytes)
        self.LOG.debug('Content_length: %s and cleanup threshold: %s', content_length, self.CLEANUP_THRESHOLD_BYTES)
        if free_bytes < (content_length + self.CLEANUP_THRESHOLD_BYTES):
            return False
        return True

    def clean_media(self, content_length):
        if not self.enough_space(content_length):
            self.run_cleanup(content_length)

    def run_cleanup(self, content_length):
        self.LOG.debug('Cleaning up old media.')
        unused_media = self.get_all_currently_unused_media()

        for media in unused_media:
            if self.enough_space(content_length + self.EXTRA_SPACE_TO_FREE_UP_BYTES):
                break
            self.LOG.debug('Removing old media: %s', media[1])
            os.remove(media[1])

        if not self.enough_space(content_length):
            raise Exception("Could not free up enough space")

    def get_all_currently_unused_media(self):
        current_media_files = []
        stored_playlist = self.PLAYLIST_PARSER.get_stored_playlist()
        if stored_playlist and len(stored_playlist):
            for media in stored_playlist:
                if media.content_type == Media.WEB_PAGE:
                    continue
                media_filepath = media.content_uri
                current_media_files.append(media_filepath)
        all_files = [os.path.join(self.MEDIA_FOLDER, file) for file in os.listdir(self.MEDIA_FOLDER)]
        unused_files = []
        for file in all_files:
            file = file.encode('UTF-8')
            if not file in current_media_files:
                pair = (os.stat(file)[ST_ATIME], file)
                unused_files.append(pair)

        unused_files = sorted(unused_files)

        self.LOG.debug('Found unused media files: %s' % unused_files)
        return unused_files

'''
if __name__ == '__main__':
    START_PATH = os.path.dirname(os.path.realpath(__file__))
    CONFIG_PATH = os.path.join(START_PATH, 'client.properties')
    config = ConfigParser.ConfigParser()
    with open(CONFIG_PATH) as config_fp:
        config.readfp(config_fp)
    cleaner = MediaCleaner(config)
    cleaner.clean_media()
'''
