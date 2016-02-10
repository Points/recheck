import collections
import sys

import click
from recheck import requirements, textui


@click.option('-r', '--requirements-file', metavar='PATH_TO_REQUIREMENTS_FILE',
              help='path to the requirements file')
@click.option('-i', '--ignore-file', metavar='PATH_TO_IGNORE_FILE',
              default='.recheckignore',
              help='path to the recheckignore file')
@click.command()
def main(requirements_file, ignore_file):
    if not requirements_file:
        raise click.BadOptionUsage('Must provide requirements file')

    click.echo('Fetching latest package info...')

    outdated_requirements = collections.defaultdict(list)
    for req in requirements.check_requirements(requirements_file, ignore_file):
        outdated_requirements[req.status].append(req)

    for req in outdated_requirements['outdated:minor']:
        textui.display(req)

    for req in outdated_requirements['outdated:minor']:
        textui.display(req)

    if outdated_requirements['outdated:minor'] or outdated_requirements['outdated:major']:
        sys.exit(1)

    sys.exit(0)
