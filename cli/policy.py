import os, click
@click.group()
def policy(): ...

@policy.command("div0")
@click.option("--set", "mode", type=click.Choice(["tend","raise","nan"]), required=True)
def div0(mode):
    os.environ["TERNLANG_DIV0_POLICY"] = mode
    click.echo(f"DIV0 policy -> {mode}")
