import server

appType='Chinese Chess'

Server=server.Server
Config=server.Config

try:
    import client
    Client=client.Client
except ImportError:
    pass
