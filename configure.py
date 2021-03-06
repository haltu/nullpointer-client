'''
Command line utility for setting the client properties.
'''

import os
import ConfigParser
from optparse import OptionParser
import readline
import glob

PROPERTIES_FILE_PATH = './client/client.properties'

CONFIG_ITEMS = (
    {
        'section': 'Storage',
        'item': 'media_folder',
        'description': 'Enter the folder where the media is downloaded to',
        'default': 'media/',
        'is_path': True
    },
    {
        'section': 'Storage',
        'item': 'playlist_file',
        'description': 'Enter the filename of the JSON playlist',
        'default': 'playlist/playlist.json',
        'is_path': True
    },
    {
        'section': 'Storage',
        'item': 'cleanup_threshold_mb',
        'description': 'Enter the number of megabytes for media to keep available',
        'default': '1',
        'is_path': False
    },
    {
        'section': 'Storage',
        'item': 'cleanup_extra_space_to_free_up_mb',
        'description': 'Amount of space to free up on top of download size and threshold.',
        'default': '100',
        'is_path': False
    },
    {
        'section': 'Device',
        'item': 'device_id_file',
        'description': 'Enter the filepath to the device id file',
        'default': 'client/device_id.devid',
        'is_path': True
    },
    {
        'section': 'Client',
        'item': 'playlist_poll_time',
        'description': 'Enter how often a new playlist is fetched (seconds)',
        'default': '60',
        'is_path': False
    },
    {
        'section': 'Server',
        'item': 'server_url',
        'description': 'Enter the URL to fetch playlists from.',
        'default': 'http://drajala.ddns.net:8000/',
        'is_path': False
    },
    {
        'section': 'Server',
        'item': 'status_server_path',
        'description': 'Enter the path on the server to send status to.',
        'default': '/api/device/status',
        'is_path': False
    },
    {
        'section': 'Server',
        'item': 'playlist_server_path',
        'description': 'Enter the path on the server to fetch playlists from and post confirmation after it has been taken to use.',
        'default': '/api/device/playlist',
        'is_path': False
    },
    {
        'section': 'Client',
        'item': 'playlist_connection_timeout',
        'description': 'Enter time to wait for a connection while downloading a playlist before giving up. (0 waits forever)',
        'default': '60',
        'is_path': False
    },
    {
        'section': 'Client',
        'item': 'playlist_bytes_timeout',
        'description': 'Enter time to wait for a single byte while downloading a playlist before giving up. (0 waits forever)',
        'default': '30',
        'is_path': False
    },
    {
        'section': 'Client',
        'item': 'status_connection_timeout',
        'description': 'Enter time to wait for a connection while posting a status message before giving up. (0 waits forever)',
        'default': '60',
        'is_path': False
    },
    {
        'section': 'Client',
        'item': 'status_bytes_timeout',
        'description': 'Enter time to wait for a single byte while posting a status message before giving up. (0 waits forever)',
        'default': '30',
        'is_path': False
    }

)


def complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def setup_autocomplete():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)


def create_properties_with_default_values():
    '''
    Creates .properties file with default values
    :return:
    '''
    config_path = PROPERTIES_FILE_PATH
    if os.path.isfile(config_path):
        user_input = raw_input('Properties file found. Are you sure you want to override it with default config? (yes/no)> ')
        if user_input != 'yes':
            return
    config = ConfigParser.ConfigParser()

    for item in CONFIG_ITEMS:
        section = item['section']
        config_item = item['item']
        value = item['default']
        if item['is_path']:
            value = os.path.join(os.path.dirname(os.path.realpath(__file__)), value)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, config_item, value)

    config_file = open(config_path, 'w+')
    config.write(config_file)
    config_file.close()
    print 'Default configuration created successfully'


def set_properties_from_user_input():
    '''
    Asks user input for properties values.
    Needs a properties file to have been created earlier
    :return:
    '''
    setup_autocomplete()
    try:
        config_path = PROPERTIES_FILE_PATH
        config_file = open(config_path, 'r')

        config = ConfigParser.ConfigParser()
        config.readfp(config_file)

        done_count = 1
        print '\nPress enter to use the default value or enter your own'
        for item in CONFIG_ITEMS:
            section = item['section']
            config_item = item['item']
            default_val = config.get(section, config_item)
            print '\n' + item['description']
            value = raw_input('%s/%s) Default [%s]> ' % (done_count, len(CONFIG_ITEMS), default_val)).strip()
            if len(value) == 0:
                value = default_val
            config.set(section, config_item, value)
            done_count += 1

        config_file.close()
        config_file = open(config_path, 'w')
        config.write(config_file)
        config_file.close()
        print '\nSaved config to %s' % os.path.abspath(config_path)

    except Exception, e:
        print e
        print "Your config file is messed up. Please run configure with flag --default"


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-d',
        '--default',
        dest='default',
        action='store_true',
        default=False,
        help='Create default properties file'
    )
    parser.add_option(
        '-e',
        '--edit',
        dest='edit',
        action='store_true',
        default=False,
        help='Edit properties file'
    )
    (options, args) = parser.parse_args()
    if options.default:
        create_properties_with_default_values()
    if options.edit:
        set_properties_from_user_input()
    if not options.edit and not options.default:
        parser.print_help()
