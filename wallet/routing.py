from channels.routing import route
from .consumers import ws_connect, ws_disconnect, receivess

channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.receive', receivess),
    route('websocket.disconnect', ws_disconnect),
]
