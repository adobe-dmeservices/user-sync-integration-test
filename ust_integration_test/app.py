import click
from click_default_group import DefaultGroup


@click.group(cls=DefaultGroup, default='run', default_if_no_args=True, help="help text")
@click.pass_context
def cli(ctx):
    ctx.obj = {'help': ctx.get_help()}


@cli.command(
    help="Start the process",
    context_settings=dict(max_content_width=400))
@click.pass_context
def run(ctx):
    pass


if __name__ == '__main__':
    cli()
