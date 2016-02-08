import click
from recheck import requirements as r


@click.option('-r', '--requirements-file', metavar='PATH',
              help='path to the requirements file')
@click.command()
def main(requirements_file):
    if not requirements_file:
        raise click.BadOptionUsage('Must provide requirements file')

    package_finder, requirements = r.get_requirements_map(requirements_file)
    outdated_requirements = r.get_oudated_requirements(index_urls=package_finder.index_urls)
    for dist, remote_version_raw, remote_version_parsed in outdated_requirements:
        direct_dependency = requirements.get(dist.key)
        if direct_dependency:
            print('Oudated: {} Installed: {} Latest: {}'.format(
                dist.key, dist.version, remote_version_raw
            ))
