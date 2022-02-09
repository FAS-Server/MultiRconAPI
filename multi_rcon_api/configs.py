from typing import Dict, List

from mcdreforged.utils.serializer import Serializable


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
