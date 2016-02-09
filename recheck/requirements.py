import os

from pip.commands import list as pip_list
from pip import req as pip_req
from pip import index as pip_index
from pip import download as pip_download


def get_requirements_map(requirements_file):
    """Get a map of requirements from the pip requirements file.
    """
    session = pip_download.PipSession()
    package_finder = pip_index.PackageFinder([], [], session=session)
    requirements = pip_req.parse_requirements(requirements_file,
                                              finder=package_finder,
                                              session=session)
    return package_finder, {r.name: r for r in requirements}


def get_oudated_requirements(index_urls=[]):
    cmd = pip_list.ListCommand()
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


def get_ignored_requirements(ignore_file):
    if not os.path.exists(ignore_file):
        return set([])

    with open(ignore_file) as f:
        return set(f.readlines())
