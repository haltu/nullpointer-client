'''
Command line utility which installs all the requirements (APT and pip)
Use the -c (or --configure) switch to also configure after installation
of requirements.

Requires superuser priviledges
'''

import os
import stat
import subprocess
import sys
import pip
import ConfigParser
import configure
from optparse import OptionParser

APT_REQS = (
    'python-pip',
    'matchbox-window-manager',
    'uzbl',
    'xinit'
)

PIP_REQS = (
   'sh==1.11',
)

DEVNULL = open(os.devnull, 'wb')


def install_apt_req(apt_req):
    retval = subprocess.call(
        ['apt-get', 'install', apt_req, '-y'],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def is_apt_pkg_installed(apt_req):
    retval = subprocess.call(
        ['dpkg', '-s', apt_req],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def install_pip_req(pip_req):
    retval = subprocess.call(
        ['pip', 'install', pip_req],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def is_pip_req_installed(req):
    return req in sys.modules


def install_reqs(reqs, is_installed_func, install_func):
    pkg_count = 0
    for req in reqs:
        if is_installed_func(req):
            status = 'Already installed'
        else:
            install_ok = install_func(req)
            if not install_ok:
                status = 'Installation failed'
            else:
                status = 'Installation successful'
        pkg_count += 1
        print '%s/%s) %s: %s' % (pkg_count, len(reqs), req, status)


def add_to_startup():
    user = 'pi' # Should this be configurable?
    start_path = os.path.dirname(os.path.realpath(__file__)) + '/start.sh'
    cron_line = '@reboot %s xinit %s &' % (user, start_path)
    cron_file = open('/etc/crontab', 'r')
    cron_content = cron_file.read()
    cron_file.close()
    if cron_line in cron_content:
        return
    cron_file = open('/etc/crontab', 'a')
    cron_file.write(cron_line)
    cron_file.close()


def install():
    print 'Installing APT packages...'
    install_reqs(APT_REQS, is_apt_pkg_installed, install_apt_req)
    print '\nInstalling python packages...'
    install_reqs(PIP_REQS, is_pip_req_installed, install_pip_req)
    print '\nAdding client to startup programs'
    add_to_startup()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-c', 
        '--configure',
        dest='configure',
        action='store_true', 
        default=False, 
        help='Configure client properties after installation'
    )
    (options, args) = parser.parse_args()
    
    install()
    if options.configure:
        configure.configure()
    DEVNULL.close()
