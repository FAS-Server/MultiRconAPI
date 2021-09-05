# Multi Rcon API

[English](./README_EN.md) | 简体中文


一个使用rcon来做到对群组服进行简单操作的api


## 依赖

MCDReforged: >=2.1.2

## 配置

`broadcast `: 是否将特定事件通过rcon进行广播, 其中 `startup`为服务器启动事件,  `stop` 为服务器关闭事件

`servers` : 存储群组服务器中所有的rcon信息, 键为服务器名, 建议与跨服中的名称保持一致；值为rcon的 地址/端口/ 密码 等信息

`self_server`: 存储此子服务器名称, 用于在通过rcon广播事件时作为标识

`groups`: 存储自定义服务器分组信息

示例配置文件如下:

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

