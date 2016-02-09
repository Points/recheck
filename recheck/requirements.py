import collections
import os

from pip.commands import list as pip_list
from pip import req as pip_req
from pip import index as pip_index
from pip import download as pip_download


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


OutdatedRequirement = collections.namedtuple('OutdatedRequirement',
                                             ['name', 'installed_version', 'latest_version'])


def check_requirements(requirements_file, ignore_file):
    result = collections.defaultdict(list)

    package_finder, requirements = _get_requirements_map(requirements_file)
    outdated_requirements = _get_oudated_requirements(index_urls=package_finder.index_urls)
    ignored_requirements = _get_ignored_requirements(ignore_file)
    for dist, remote_version_raw, remote_version_parsed in outdated_requirements:
        direct_dependency = requirements.get(dist.key)
        if not direct_dependency:
            continue

        outdated_dependency = OutdatedRequirement(dist.key, dist.version, remote_version_raw)

        if direct_dependency.name in ignored_requirements:
            result['ignored'].append(outdated_dependency)
        else:
            result['outdated'].append(outdated_dependency)

    return result
