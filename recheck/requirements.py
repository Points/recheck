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
        self._requirements_files = collections.deque([requirements_file])
        self._direct_requirements = set()
        self._index_url = None
        self._extra_index_urls = []
        self._parse()

    def _handle_comment(self, line):
        return

    def _handle_pip_directive(self, line):
        directive, value = re.split('\s+|=', line)
        if directive == '-r':
            self._requirements_files.append(value)
        if directive == '--index-url':
            self._index_url = value
        if directive == '--extra-index-url':
            self._extra_index_urls.append(value)
        if directive == '-e':
            raise NotImplementedError()

    def _handle_requirement_line(self, line):
        result = re.split('==|>|<|>=|<=', line)
        req = result[0]
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


def _get_ignored_requirements(ignore_file):
    if not os.path.exists(ignore_file):
        return set([])

    with open(ignore_file) as f:
        return set(map(str.strip, f.readlines()))


def check_requirements(requirements_file, ignore_file):
    package_finder, requirements = _get_requirements_map(requirements_file)
    outdated_requirements = _get_oudated_requirements(index_urls=package_finder.index_urls)
    ignored_requirements = _get_ignored_requirements(ignore_file)
    for package in outdated_requirements:
        direct_requirement = requirements.get(package.name)

        if not direct_requirement:
            continue

        yield OutdatedRequirement(direct_requirement, package.installed_version,
                                  package.remote_version, ignored_requirements)
