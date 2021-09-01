from typing import Dict, List, Optional

from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.utils import Serializable
from mcdreforged.api.types import PluginServerInterface, CommandSource
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.command import Literal, Text


class ServerConfig(Serializable):
    address: str = "localhost"
    port: int = 25565
    password: str = "default_password_please_change"


class Config(Serializable):
    debug: bool = False
    servers: Dict[str, ServerConfig] = {
        'Survival': ServerConfig(port=25565),
        'Mirror': ServerConfig(port=25566),
        'Creative': ServerConfig(port=25567)
    }

    groups: Dict[str, List[str]] = {}


class Rcon(RconConnection):
    def __init__(self, config: ServerConfig):
        super().__init__(**config.serialize())


class MultiRcon:
    def __init__(self, server: PluginServerInterface):
        self.config = server.load_config_simple(target_class=Config)

    def get_servers(self, group: Optional[str] = None):
        if group is None:
            return self.config.servers.keys()

        elif group in self.config.groups:
            return self.config.groups.get(group)

        else:
            raise TypeError(f'The group {group} is not in list')

    def group_command(self, command, group: Optional[str] = None):
        target_servers = self.get_servers(group)
        ret: dict = {}
        for server in target_servers:
            ret_unit = {}
            try:
                session = Rcon(self.config.servers.get(server))
                ret_unit['connected'] = session.connect()
                data = session.send_command(command)
                if ret_unit['connected'] and data:
                    ret_unit['data'] = data
                else:
                    ret_unit['data'] = ''
            except:
                ret_unit = {}
            ret[server] = ret_unit
        return ret



multi_rcon_instance: Optional[MultiRcon] = None


@new_thread()
def send_multi_command(command: str, group: Optional[str] = None, src: Optional[CommandSource] = None):
    if multi_rcon_instance:
        ret = multi_rcon_instance.group_command(command, group)
        if src:
            src.reply(str(ret))
        return ret
    else:
        raise RuntimeWarning('Cannot send command before init!')


def on_load(server: PluginServerInterface, old):
    global multi_rcon_instance
    multi_rcon_instance = MultiRcon(server)
    config = multi_rcon_instance.config
    if config.debug:
        server.register_command(
            Literal('!!rcon').requires(lambda src: src.has_permission(2)).runs(lambda src: src.reply(str(config.serialize())))
            .then(
                Text('cmd').runs(lambda src, ctx: send_multi_command(ctx['cmd'], src=src)).then(
                    Text('group').runs(lambda src, ctx: send_multi_command(ctx['cmd'], ctx['group'], src))
                )
            )
        )
