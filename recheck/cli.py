import subprocess

import click
from recheck import requirements


@click.option('-r', '--requirements-file', metavar='PATH_TO_REQUIREMENTS_FILE',
              help='path to the requirements file')
@click.option('-i', '--ignore-file', metavar='PATH_TO_IGNORE_FILE',
              default='.recheckignore',
              help='path to the recheckignore file')
@click.command()
def main(requirements_file, ignore_file):
    if not requirements_file:
        raise click.BadOptionUsage('Must provide requirements file')

    requirements_parser = requirements.RequirementsParser(requirements_file)
    direct_requirements = requirements_parser.direct_requirements
    index_urls = requirements_parser.extra_index_urls

    # parse the requirements file to get the index-urls
    proc = subprocess.Popen(['pip', 'list', '--outdated'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    sentinel = ''
    for line in iter(proc.stdout.readline, sentinel):
        print line

    for line in iter(proc.stderr.readline, sentinel):
        print line
