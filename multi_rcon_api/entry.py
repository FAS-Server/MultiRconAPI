from typing import Optional

from mcdreforged.api.types import PluginServerInterface, CommandSource
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.command import Literal, Text, GreedyText

from multi_rcon_api.multi_rcon import Config, MultiRcon


__instance: Optional[MultiRcon] = None


def tr(server: PluginServerInterface, translation_key: str, *args, **kwargs):
    return PluginServerInterface.tr(server, f'multi_rcon_api.{translation_key}', *args, **kwargs)


def rtr(server: PluginServerInterface, translation_key: str, *args, **kwargs):
    return PluginServerInterface.rtr(server, f'multi_rcon_api.{translation_key}', *args, **kwargs)


@new_thread("multi_rcon_api:multi_command")
def send_multi_command(src: CommandSource, command: str, group: Optional[str] = None):
    if __instance:
        ret = __instance.group_command(command, group)
        src.reply(str(ret))
    else:
        raise RuntimeWarning('Cannot send command before init!')


@new_thread("multi_rcon_api:single_command")
def send_single_command(src: CommandSource, command: str, server: str):
    if __instance:
        ret = __instance.single_command(command, server)
        src.reply(ret)
    else:
        raise RuntimeWarning('Cannot send command before init!')


def register_debug_command(server: PluginServerInterface, config: Config):
    meta = server.get_self_metadata()
    general_help = rtr(server, 'debug.general_help', prefix='!!rcon', version=meta.version)

    debug_node = Literal('!!rcon').requires(lambda src: src.has_permission(2)).runs(
        lambda src: src.reply(general_help)).then(
        Literal({'config', 'cfg'}).runs(lambda src: src.reply(str(config.serialize())))
    ).then(
        Literal('run').then(
            Literal('-s').then(Text('server').then(GreedyText('cmd').runs(
                lambda src, ctx: send_single_command(src, ctx['cmd'], ctx['server'])))
        )).then(
            Literal('-g').then(Text('group').then(GreedyText('cmd').runs(
                lambda src, ctx: send_multi_command(src, ctx['cmd'], ctx['group']))))
        ).then(GreedyText('cmd').runs(lambda src, ctx: send_multi_command(src, ctx['cmd'])))
    )
    server.register_command(debug_node)


def on_load(server: PluginServerInterface, old):
    global __instance
    if hasattr(old, '__instance'):
        __instance = old.__instance
        __instance.reload()
    else:
        __instance = MultiRcon(server)
    config = __instance.config
    if config.debug:
        register_debug_command(server, config)


def on_unload(server: PluginServerInterface):
    if __instance:
        __instance.clear()


@new_thread('multi_rcon_api#broadcast_startup')
def on_server_startup(server: PluginServerInterface):
    config = __instance.config
    if config.Broadcast.startup:
        msg = tr(server, 'broadcast.startup', config.self_server)
        __instance.group_command(msg)


@new_thread('multi_rcon_api#broadcast_stop')
def on_server_stop(server: PluginServerInterface, code: int):
    config = __instance.config
    if config.Broadcast.stop:
        msg = tr(server, 'broadcast.stop', server_name=config.self_server, error_code=code)
        __instance.group_command(msg)
