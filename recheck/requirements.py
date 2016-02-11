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
        self._requirements_files = [requirements_file]
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
        lines = _read_lines_from_file(self._requirements_files[0])
        for line in lines:
            if line.startswith('#'):
                self._handle_comment(line)
            elif line.startswith('-'):
                self._handle_pip_directive(line)
            else:
                self._handle_requirement_line(line)

    @property
    def direct_requirements(self):
        return self._direct_requirements

    @property
    def index_url(self):
        return self._index_url

    @property
    def extra_index_urls(self):
        return self._extra_index_urls


class OutdatedRequirement(object):
    def __init__(self, requirement, installed_version, remote_version,
                 ignored_requirements):
        self._requirement = requirement
        self._name = requirement.name
        self._installed_version = installed_version
        self._remote_version = remote_version
        self._ignored_requirements = ignored_requirements

    @property
    def status(self):
        if self._name in self._ignored_requirements:
            return 'ignored'

        if self._installed_version[0] == self._remote_version[0]:
            return 'outdated:minor'
        else:
            return 'outdated:major'

    @staticmethod
    def _format_version(parsed_version):
        parts = []
        for part in parsed_version:
            if part == '*final':  # *final is a marker, not part of the version
                continue
            try:
                parts.append(str(int(part)))
            except ValueError:
                parts.append(part)

        return '.'.join(parts)

    def __str__(self):
        return '{name}  Installed: {installed_version}  Latest: {latest_version}'.format(
            name=self._name,
            installed_version=self._format_version(self._installed_version),
            latest_version=self._format_version(self._remote_version),
        )


class Package(object):
    def __init__(self, distribution, remote_version):
        self._distribution = distribution
        self._remote_version = remote_version

    @property
    def name(self):
        return self._distribution.key

    @property
    def installed_version(self):
        return self._distribution.parsed_version

    @property
    def remote_version(self):
        return self._remote_version

    def is_outdated(self):
        return self._distribution.parsed_version != self._remote_version


class PipListCommand(pip_list.ListCommand):
    def find_latest_versions(self, options):
        # The public API for pip's ListCommand has changed dramatically (both
        # in name and return value) so this adaptor is needed to hide the
        # underlying pip details from the calling code.
        if hasattr(self, 'find_packages_latests_versions'):
            for latest_version in self.find_packages_latests_versions(options):
                if not isinstance(latest_version, tuple):
                    raise TypeError()

                if len(latest_version) == 2:
                    # pip 6
                    dist, remote_version = latest_version
                    yield Package(dist, remote_version)

                if len(latest_version) == 3 and isinstance(latest_version[-1], basestring):
                    # pip 7
                    dist, remote_version_parsed, _ = latest_version
                    yield Package(dist, remote_version_parsed)

                else:
                    # assume pip 1.5
                    dist, remote_version_raw, remote_version_parsed = latest_version
                    yield Package(dist, remote_version_parsed)

        elif hasattr(self, 'find_packages_latest_versions'):
            # pip 8+
            for dist, remote_version, type in self.find_packages_latest_versions(options):
                yield Package(dist, remote_version)
        else:
            raise RuntimeError('The version of pip installed does not support '
                               'getting latest versions of requirements')


def _get_requirements_map(requirements_file):
    """Get a map of requirements from the pip requirements file.
    """
    session = pip_download.PipSession()
    package_finder = pip_index.PackageFinder([], [], session=session)
    requirements = pip_req.parse_requirements(requirements_file,
                                              finder=package_finder,
                                              session=session)
    return package_finder, {r.name: r for r in requirements}


def _get_oudated_requirements(index_urls=[]):
    cmd = PipListCommand()
    args = ['--outdated']

    if index_urls:
        index_url, extra_index_urls = index_urls[0], index_urls[1:]
        args.extend(['--index-url', index_url])
        for index_url in extra_index_urls:
            args.extend(['--extra-index-url', index_url])

    options, _ = cmd.parse_args(args)

    return (package for package in cmd.find_latest_versions(options)
            if package.is_outdated())


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
