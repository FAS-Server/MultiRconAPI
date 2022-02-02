import struct
from threading import Lock
from typing import Dict, List, Optional

from mcdreforged.api.decorator import new_thread
from mcdreforged.api.utils import Serializable
from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.types import PluginServerInterface


class ServerConfig(Serializable):
    address: str = "localhost"
    port: int = 25575
    password: str = "default_password_please_change"


class ServerList(Serializable):
    servers: Dict[str, ServerConfig] = {
        'Survival': ServerConfig(port=25565),
        'Mirror': ServerConfig(port=25566),
        'Creative': ServerConfig(port=25567)
    }
    groups: Dict[str, List[str]] = {}


class Config(Serializable):
    class Broadcast:
        startup: bool = True
        stop: bool = True
    debug: bool = False
    data_file: str = "config/MultiRconAPI_ServerList.json"
    self_server: str = 'Survival'


class Rcon(RconConnection):
    def __init__(self, config: ServerConfig):
        super().__init__(**config.serialize())

    def safe_connect(self) -> bool:
        try:
            return self.connect()
        except struct.error:
            self.socket = None
            return False

    def safe_command(self, command: str, max_retry_time: int = 5) -> Optional[str]:
        if max_retry_time <= 0:
            return
        elif self.socket is None:
            self.safe_connect()
            return self.safe_command(command, max_retry_time - 1)
        else:
            return self.send_command(command=command, max_retry_time=1)


class MultiRcon:
    __instance_lock = Lock()
    __instance: Optional['MultiRcon'] = None

    def __init__(self, server: PluginServerInterface):
        self.__server = server
        self.rcons: Dict[str, Rcon] = {}  # for holding up the rcon connections
        self.config: Optional[Config] = self.__server.load_config_simple(target_class=Config)
        self.server_data: Optional[ServerList] = None
        self.reload()

    @new_thread("MultRconAPI#reload")
    def reload(self):
        self.clear()
        self.config = self.__server.load_config_simple(target_class=Config)
        self.server_data = self.__server.load_config_simple(
            file_name=self.config.data_file, in_data_folder=False, target_class=ServerList)
        for server_name in self.server_data.servers:
            rcon_instance = Rcon(self.server_data.servers.get(server_name))
            self.rcons[server_name] = rcon_instance
            try:
                rcon_instance.safe_connect()
            except ConnectionRefusedError:
                self.__server.logger.info(f"Can't connect to {server_name}")

    def __new__(cls, *args, **kwargs):  # for singleton instance
        if not cls.__instance:
            with cls.__instance_lock:
                if not cls.__instance:
                    cls.__instance = object.__new__(cls)
        return cls.__instance

    def clear(self):
        server_list = self.rcons.keys()[:]
        for server_name in server_list:
            self.rcons.pop(server_name)

    @classmethod
    def get_instance(cls):
        return cls.__instance

    def get_servers(self, group: Optional[str] = None):
        if group is None:
            return self.server_data.servers.keys()

        elif group in self.server_data.groups:
            return self.server_data.groups.get(group)

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
        if server in self.server_data.servers:
            rcon = self.rcons.get(server)
            if rcon is None:
                rcon = Rcon(self.server_data.servers.get(server))
                self.rcons[server] = rcon
            payload = rcon.safe_command(command)
            return {'connected': rcon.socket is not None and payload is not None, 'data': payload}
        else:
            return {'connected': False, 'data': 'No Such Server in Config'}

    def check_new_thread(self):
        if self.__server.is_on_executor_thread():
            raise RuntimeError('Should run in new thread!')
