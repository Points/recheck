from pip.commands import list as pip_list
from pip import req as pip_req
from pip import index as pip_index


def list_oudated_requirements():
    cmd = pip_list.ListCommand()
    options, _ = cmd.parse_args(['--outdated'])
    return (
        (dist, remote_version_raw, remote_version_parsed)
        for dist, remote_version_raw, remote_version_parsed in cmd.find_packages_latests_versions(options)
        if dist.parsed_version != remote_version_parsed
    )


def main():
    finder = pip_index.PackageFinder(None, None)
    requirements = pip_req.parse_requirements('requirements/development.txt', finder=finder)
    # for requirement in requirements:
    # pass

    # for dist, remote_version_raw, remote_version_parsed in list_oudated_requirements():
    #     print(dist)
