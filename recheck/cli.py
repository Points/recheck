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

    args = ['pip', 'list', '--outdated']
    if requirements_parser.index_url:
        args.append('--index-url={}'.format(requirements_parser.index_url))

    if requirements_parser.extra_index_urls:
        for index_url in requirements_parser.extra_index_urls:
            args.append('--extra-index-url={}'.format(index_url))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    sentinel = ''
    for line in iter(proc.stdout.readline, sentinel):
        req = requirements.parse_result(line)
        if req:
            if req.name in requirements_parser.direct_requirements:
                print(req)
