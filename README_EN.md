# Multi Rcon API

![MCDReforged](https://img.shields.io/badge/dynamic/json?label=MCDReforged&query=dependencies.mcdreforged&url=https%3A%2F%2Fraw.githubusercontent.com%2FFAS-Server%2FMultiRconAPI%2Fmaster%2Fmcdreforged.plugin.json&style=plastic) ![license](https://img.shields.io/github/license/FAS-Server/MultiRconAPI?style=plastic) ![build status](https://img.shields.io/github/workflow/status/FAS-Server/MultiRconAPI/CI%20for%20MCDR%20Plugin?label=build&style=plastic) ![Release](https://img.shields.io/github/v/release/FAS-Server/MultiRconAPI?style=plastic) ![total download](https://img.shields.io/github/downloads/FAS-Server/MultiRconAPI/total?label=total%20download&style=plastic)

English| [简体中文](./README.md)

An api to make it easier to control group server by rcon

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

