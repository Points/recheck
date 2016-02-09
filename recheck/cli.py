import click
from recheck import requirements as r


@click.option('-r', '--requirements-file', metavar='PATH_TO_REQUIREMENTS_FILE',
              help='path to the requirements file')
@click.option('-i', '--ignore-file', metavar='PATH_TO_IGNORE_FILE',
              default='.recheckignore',
              help='path to the recheckignore file')
@click.command()
def main(requirements_file, ignore_file):
    if not requirements_file:
        raise click.BadOptionUsage('Must provide requirements file')

    package_finder, requirements = r.get_requirements_map(requirements_file)
    outdated_requirements = r.get_oudated_requirements(index_urls=package_finder.index_urls)
    ignored_requirements = r.get_ignored_requirements(ignore_file)
    for dist, remote_version_raw, remote_version_parsed in outdated_requirements:
        direct_dependency = requirements.get(dist.key)
        if direct_dependency and direct_dependency not in ignored_requirements:
            print('Oudated: {} Installed: {} Latest: {}'.format(
                dist.key, dist.version, remote_version_raw
            ))
