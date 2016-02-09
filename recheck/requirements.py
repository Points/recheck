import os

from pip.commands import list as pip_list
from pip import req as pip_req
from pip import index as pip_index
from pip import download as pip_download


class OutdatedRequirement(object):
    def __init__(self, requirement, installed_version, remote_version, ignored_requirements):
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


class PipListCommand(pip_list.ListCommand):
    def find_packages_latest_versions(self, *args, **kwargs):
        if hasattr(pip_list.ListCommand, 'find_packages_latest_versions'):
            return super(PipListCommand, self).find_packages_latest_versions(*args, **kwargs)
        elif hasattr(self, 'find_packages_latests_versions'):
            return self.find_packages_latests_versions(*args, **kwargs)
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
    return (
        (dist, remote_version_raw, remote_version_parsed)
        for dist, remote_version_raw, remote_version_parsed
        in cmd.find_packages_latest_versions(options)
        if dist.parsed_version != remote_version_parsed
    )


def _get_ignored_requirements(ignore_file):
    if not os.path.exists(ignore_file):
        return set([])

    with open(ignore_file) as f:
        return set(map(str.strip, f.readlines()))


def check_requirements(requirements_file, ignore_file):
    package_finder, requirements = _get_requirements_map(requirements_file)
    outdated_requirements = _get_oudated_requirements(index_urls=package_finder.index_urls)
    ignored_requirements = _get_ignored_requirements(ignore_file)
    for dist, remote_version_raw, remote_version_parsed in outdated_requirements:
        direct_requirement = requirements.get(dist.key)

        if not direct_requirement:
            continue

        yield OutdatedRequirement(direct_requirement, dist.parsed_version, remote_version_parsed, ignored_requirements)
