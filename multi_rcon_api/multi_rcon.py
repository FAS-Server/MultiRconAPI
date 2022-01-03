from threading import Lock
from typing import Dict, List, Optional

from mcdreforged.api.utils import Serializable
from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.types import PluginServerInterface


class ServerConfig(Serializable):
    address: str = "localhost"
    port: int = 25575
    password: str = "default_password_please_change"


class Config(Serializable):
    class Broadcast:
        startup: bool = True
        stop: bool = True
    debug: bool = False
    servers: Dict[str, ServerConfig] = {
        'Survival': ServerConfig(port=25565),
        'Mirror': ServerConfig(port=25566),
        'Creative': ServerConfig(port=25567)
    }

    self_server: str = 'Survival'

    groups: Dict[str, List[str]] = {}


class Rcon(RconConnection):
    def __init__(self, config: ServerConfig):
        super().__init__(**config.serialize())


class MultiRcon:
    __instance_lock = Lock()
    __instance: Optional['MultiRcon'] = None

    def __init__(self, server: PluginServerInterface):
        self.__server = server
        self.rcons: Dict[str, Rcon] = {}  # for holding up the rcon connections
        self.config: Optional[Config] = None
        self.reload()

    def reload(self):
        self.clear()
        self.config = self.__server.load_config_simple(target_class=Config)
        for server_name in self.config.servers:
            rcon_instance = Rcon(self.config.servers.get(server_name))
            self.rcons[server_name] = rcon_instance
            rcon_instance.connect()

    def __new__(cls, *args, **kwargs):  # for singleton instance
        if not cls.__instance:
            with cls.__instance_lock:
                if not cls.__instance:
                    cls.__instance = object.__new__(cls)
        return cls.__instance

    def clear(self):
        for server_name in self.rcons:
            self.rcons.pop(server_name)

    @classmethod
    def get_instance(cls):
        return cls.__instance

    def get_servers(self, group: Optional[str] = None):
        if group is None:
            return self.config.servers.keys()

        elif group in self.config.groups:
            return self.config.groups.get(group)

        else:
            raise RuntimeWarning('No such group')

    def group_command(self, command, group: Optional[str] = None):
        self.check_new_thread()
        target_servers = self.get_servers(group)
        ret: dict = {}
        for server in target_servers:
            ret[server] = self.single_command(command, server)
        return ret

    def single_command(self, command: str, server: str):
        self.check_new_thread()
        if server in self.config.servers:
            return self.rcons.get(server).send_command(command, max_retry_time=5)
        else:
            return 'No Such Server in Config'

    def check_new_thread(self):
        if self.__server.is_on_executor_thread():
            raise RuntimeError('Should run in new thread!')
