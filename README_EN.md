# Multi Rcon API

English| [简体中文](./README.md)


An api to make it easier to control group server by rcon

## Dependencies

MCDReforged: >=2.1.2

## Config

 `broadcast `: Whether to broadcast startup and stop event through rcon

`servers` : The rcon info of all the group servers, key for server name, suggested to set as the same in the Velocity/BungeeCord, value for rcon info

`self_server`: The server name of current sub-server, used in broadcast for identification.

`groups`: The custom server group

Example config file are as follow:

```json
{
    "broadcast": {
        "startup": true,
        "stop": false
    },
    "servers": {
        "Survival": {
            "address": "localhost",
            "port": "25565",
            "password": "default_password_please_change"
        },
        "Creative": {
            "address": "localhost",
            "port": "25566",
            "password": "default_password_please_change"
        },
        "Mirror": {
            "address": "localhost",
            "port": "25567",
            "password": "default_password_please_change"
        }
    },
    "self_server": "Survival",
    "groups": {
        "g_creative": ["Creative", "Mirror"]
    }
}
```

