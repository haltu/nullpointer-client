import requests
import time
import logging
import os
import shutil
from urlparse import urlparse
import re
from hashlib import md5

class ResumableFileDownload(object):
    '''
    A utility class which downloads the data from the given url to the
    given file path. In case the download is interrupted e.g. by
    a power failure, it will cotinue downloading from the last byte stored
    on disk.

    This works by dowloading data to a '.incomplete' file. When the download is
    finished, the '.incomplete' file is copied to a regular file with the
    '.incomplete' extension removed. If the download is interrupted, the
    missing portion of the file is downloaded based on the number of bytes
    the '.incomplete' file contains.
    '''
    MD5_STRING = "md5"
    LOG = logging.getLogger(__name__)

    def __init__(self, url, media_folder, filename, md5):
        self.url = url
        filename =self.MD5_STRING + str(md5) + filename
        self.complete_filepath = os.path.join(media_folder, filename)
        self.incomplete_filepath = self.complete_filepath + '.incomplete'
        self.md5 = md5

    def is_complete(self):
        if os.path.isfile(self.complete_filepath):
            return True
        return False

    def stream_to_file(self, iter_function):
        with open(self.incomplete_filepath, 'ab') as f:
            for chunk in iter_function(chunk_size=1024):
                if not chunk: break
                f.write(chunk)

    def download_complete(self):
        if os.path.isfile(self.incomplete_filepath):
            self.LOG.debug("is a file")
            file_md5 = md5(self.incomplete_filepath).hexdigest()
            self.LOG.debug("md5: %s", file_md5)
            if(file_md5 == md5):
                os.rename(self.incomplete_filepath, self.complete_filepath)
        raise Exception("Error renaming a complete file.")

    def bytes_downloaded(self):
        if os.path.isfile(self.incomplete_filepath):
            return os.path.getsize(self.incomplete_filepath)
        return 0

class ChunkedDownloader(object):
    '''
    Downloads a file in chunks. If a chunk cannot be downloaded within a given
    timeout, the chunk download is cancelled and will be re-attempted.
    '''

    LOG = logging.getLogger(__name__)
    CHUNK_SIZE = 500000  # 500 Kb
    CHUNK_DOWNLOAD_TIMEOUT = 120  # Seconds
    RETRY_TIMEOUT = 10  # Seconds
    MEDIA_FOLDER = ""

    def __init__(self, server_url, device_id, media_folder):
        self.HISRA_NET_LOC = urlparse(server_url).netloc
        self.AUTHORIZATION_HEADER = 'Device %s' % device_id
        self.MEDIA_FOLDER = media_folder
        self.TIMEOUTS = (None, 60)


    # idea would be we download as much as we can and ResumableFileDownload handles file operations.
    # not ready. resumablefiledownload has not been changed yet.
    def download(self, content):
        url = content.content_uri
        headers = {}
        if urlparse(url).netloc == self.HISRA_NET_LOC:
            headers['Authorization'] = self.AUTHORIZATION_HEADER
        response = requests.get(
            url,
            timeout=self.TIMEOUTS,
            stream=True,
            headers=headers
        )
        filename = re.findall("filename=(.+)", response.headers['Content-Disposition'])
        filename = filename[0].strip() if len(filename) else ''
        md5 = response.headers['Content-MD5']
        resumable_download = ResumableFileDownload(url,self.MEDIA_FOLDER,filename,md5)
        if resumable_download.is_complete():
            response.close()
            return resumable_download.complete_filepath
        bytes_downloaded = resumable_download.bytes_downloaded()
        if bytes_downloaded > 0:
            response.close()
            # TODO +1 or not?
            headers['Range'] = 'bytes=%s-' % bytes_downloaded
            response = requests.get(
            url,
            timeout=self.TIMEOUTS,
            stream=True,
            headers=headers)

        resumable_download.stream_to_file(response.iter_content)

        resumable_download.download_complete()

        return resumable_download.complete_filepath