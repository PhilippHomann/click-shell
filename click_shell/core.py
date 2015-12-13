
import os
import shlex

import click

from ._cmd import ClickCmd


HIST_FILE = os.path.join(os.path.expanduser('~'), '.stackdio-cli', 'history')


def get_invoke(command):
    """
    Get the Cmd main method from the click command
    :param command: The click Command object
    :return: the do_* method for Cmd
    :rtype: function
    """

    assert isinstance(command, click.Command)

    def invoke(self, arg):
        try:
            rv = command.main(args=shlex.split(arg),
                              prog_name=command.name,
                              standalone_mode=False)
            return rv
        except click.ClickException as e:
            # Show the error message
            e.show()
        except click.Abort:
            # We got an EOF or Keyboard interrupt.  Just silence it
            pass
        except SystemExit as e:
            # Catch this an return the code instead. All of click's help commands do a sys.exit(),
            # and that's not ideal when running in a shell.
            return e.code
    return invoke


def get_help(command):
    """
    Get the Cmd help function from the click command
    :param command: The click Command object
    :return: the help_* method for Cmd
    :rtype: function
    """
    assert isinstance(command, click.Command)

    def help(self):
        extra = {}
        for key, value in command.context_settings.items():
            if key not in extra:
                extra[key] = value

        # Print click's help message
        with click.Context(command, info_name=command.name, **extra) as ctx:
            click.echo(ctx.get_help(), color=ctx.color)
    return help


def get_click_shell(command, prompt=None, intro=None):

    # Create our ClickShell class (just a pass for now in case we want to override things later)
    class ClickShell(ClickCmd):
        pass

    if prompt is not None:
        ClickShell.prompt = prompt

    if intro is not None:
        ClickShell.intro = intro

    # set all the click commands
    for name, command in command.commands.items():
        cmd_name = name.replace('-', '_')
        setattr(ClickShell, 'do_%s' % cmd_name, get_invoke(command))
        setattr(ClickShell, 'help_%s' % cmd_name, get_help(command))

    return ClickShell()
