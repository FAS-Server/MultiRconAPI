from multi_rcon_api.multi_rcon import Rcon, ServerConfig

rcon: Rcon
try:
    address = input("Please input rcon address(without port):")
    port = int(input("Please input port:"))
    password = input("Please input password:")
    rcon = Rcon(ServerConfig(address=address, port=port, password=password))
    print("Login Success? ", rcon.safe_connect())
    while True:
        print('Rcon ->', rcon.safe_command(input('Rcon <- ')))
except KeyboardInterrupt:
    exit(0)
except ValueError:
    print("Error input!")
    exit(1)
