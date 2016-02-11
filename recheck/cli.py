import subprocess
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

    requirements_parser = requirements.RequirementsParser(requirements_file)

    args = ['pip', 'list', '--outdated']
    if requirements_parser.index_url:
        args.append('--index-url={}'.format(requirements_parser.index_url))

    if requirements_parser.extra_index_urls:
        for index_url in requirements_parser.extra_index_urls:
            args.append('--extra-index-url={}'.format(index_url))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    ignored_requirements = requirements.get_ignored_requirements(ignore_file)

    ignored, outdated_major, outdated_minor = set(), set(), set()

    sentinel = ''
    for line in iter(proc.stdout.readline, sentinel):
        req = requirements.parse_result(line)
        if not req:
            # the output does not resemble an outdated requirement
            continue

        if not req.name in requirements_parser.direct_requirements:
            # not a direct requirement
            continue

        textui.progress()

        if req.name in ignored_requirements:
            ignored.add(req)

        if req.status == 'outdated:minor':
            outdated_minor.add(req)

        if req.status == 'outdated:major':
            outdated_major.add(req)

    textui.newline()

    if outdated_minor:
        textui.echo('Minor upgrades:', colour='white')

    for req in outdated_minor:
        textui.render_requirement(req, colour='yellow')

    if outdated_major:
        textui.echo('Major upgrades:', colour='white')

    for req in outdated_major:
        textui.render_requirement(req, colour='red')

    if outdated_major or outdated_minor:
        sys.exit(1)
