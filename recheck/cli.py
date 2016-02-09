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

    for req in r.check_requirements(requirements_file, ignore_file):
        if req.status == 'ignored':
            click.echo(click.style('Ignored: {}'.format(req), fg='green'))
        if req.status == 'outdated:minor':
            click.echo(click.style('Outdated: {}'.format(req), fg='red'))
        if req.status == 'outdated:major':
            click.echo(click.style('Outdated: {}'.format(req), fg='yellow'))
