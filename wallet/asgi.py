import os
import channels.asgi


#Swaping HTTP?WSGI based request for ASGI Asynchro Server Gateway interface
os.environ.setdefault("DJANGO_SETTING_MODULE", "crypto.settings")
channels_layer = channels.asgi.get_channel_layer()
