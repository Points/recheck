import click


def display(outdated_requirement):
    req = outdated_requirement
    if req.status == 'ignored':
        click.echo(click.style('Ignored: {}'.format(req), fg='green'))
    if req.status == 'outdated:minor':
        click.echo(click.style('Outdated: {}'.format(req), fg='red'))
    if req.status == 'outdated:major':
        click.echo(click.style('Outdated: {}'.format(req), fg='yellow'))
