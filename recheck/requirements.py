import collections
import os
import re

from pip.commands import list as pip_list
from pip import req as pip_req
from pip import index as pip_index
from pip import download as pip_download


def _read_lines_from_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()


class RequirementsParser(object):
    def __init__(self, requirements_file):
        self._dirname = os.path.dirname(requirements_file)
        self._requirements_files = collections.deque([requirements_file])
        self._direct_requirements = set()
        self._index_url = None
        self._extra_index_urls = []
        self._parse()

    def _handle_comment(self, line):
        return

    def _handle_pip_directive(self, line):
        directive, value = re.split('\s+|=', line, 1)
        if directive == '-r':
            filepath = value.strip()
            if not os.path.isabs(filepath):
                filepath = os.path.join(self._dirname, filepath)
            self._requirements_files.append(filepath)
        if directive == '--index-url':
            self._index_url = value.strip()
        if directive == '--extra-index-url':
            self._extra_index_urls.append(value.strip())
        if directive == '-e':
            pass  # TODO: Need to handle editable installs?

    def _handle_requirement_line(self, line):
        result = re.split('==|>|<|>=|<=', line)
        req = result[0].strip()
        if req:
            self.direct_requirements.add(req.strip())

    def _parse(self):
        try:
            while True:
                requirement_file = self._requirements_files.popleft()
                lines = _read_lines_from_file(requirement_file)
                for line in lines:
                    if line.startswith('#'):
                        self._handle_comment(line)
                    elif line.startswith('-'):
                        self._handle_pip_directive(line)
                    else:
                        self._handle_requirement_line(line)
        except IndexError:
            # No unprocessed requirements file. Parsing complete
            return None

    @property
    def direct_requirements(self):
        return self._direct_requirements

    @property
    def index_url(self):
        return self._index_url

    @property
    def extra_index_urls(self):
        return self._extra_index_urls


OutdatedRequirement = collections.namedtuple('OutdatedRequirement',
                                             ['name', 'installed_version', 'remote_version'])


Version = collections.namedtuple('Version', ['major', 'minor', 'rev'])


def parse_version(version_str):
    def int_or_str(s):
        try:
            return int(s)
        except ValueError:
            return s

    major, minor, rev = None, None, None
    parts = version_str.split('.', 3)
    if len(parts) > 0:
        major = int_or_str(parts[0])
    if len(parts) > 1:
        minor = int_or_str(parts[1])
    if len(parts) > 2:
        rev = int_or_str(parts[2])

    return Version(major, minor, rev)


def _status(self):
    installed_version =  parse_version(self.installed_version)
    remote_version = parse_version(self.remote_version)

    if installed_version.major < remote_version.major:
        return 'outdated:major'
    if installed_version.minor < remote_version.minor:
        return 'outdated:minor'
    if installed_version.rev < remote_version.rev:
        return 'outdated:rev'


OutdatedRequirement.status = property(_status)


def parse_result(line):
    try:
        name, info = line.strip().split(' ', 1)
        _, installed_version, _, remote_version = info[1:-1].split(' ')
        return OutdatedRequirement(name, installed_version, remote_version)
    except ValueError:
        return None


def get_ignored_requirements(ignore_file):
    if not os.path.exists(ignore_file):
        return set([])

    with open(ignore_file) as f:
        return set(map(str.strip, f.readlines()))
