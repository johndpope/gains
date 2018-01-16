from channels import Group
import json
from channels.auth import channel_session_user, channel_session_user_from_http
from .models import Crypto

from urllib.request import urlopen, Request
from urllib.parse import urljoin
urlmax = "https://api.coinmarketcap.com/v1/ticker/"

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': True,
        })
    })
@channel_session_user
def ws_disconnect(message):
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': False
        })
    })
    Group('users').discard(message.reply_channel)

@channel_session_user
def receivess(message):
    data = json.loads(message['text'])
    #If data['name'] == Luna update all cryptos
    boolreceive = 'update'
    if data['func'] == 'UpdateAll':
        for currency in Crypto.objects.all():
            currency.price = getPrice(currency.name)
            currency.totalvalue = float(currency.price) * float(currency.quantity)
            currency.save()
            Group('users').send({
                'text':json.dumps({
                    'name': currency.name,
                    'quantity': currency.quantity,
                    'price': round(float(currency.price),2),
                    'total': round(float(currency.totalvalue),2),
                    'boolreceive': boolreceive,
                })
            })

    elif data['func'] == 'delete':
        currency = Crypto.objects.get(name=data['name']).delete()
        Group('users').send({'text':json.dumps({'name': data['name'],'boolreceive': 'deleted'})})

    elif data['func'] == 'new':
        price = getPrice(data['name'])
        value = float(data['quantity']) * price
        currency = Crypto.objects.create(name=data['name'], quantity=data['quantity'], price=price, totalvalue=value)
        currency.save()
        boolreceive = 'new'
        Group('users').send({
            'text':json.dumps({
                'name': currency.name,
                'quantity': currency.quantity,
                'price': round(float(currency.price),2),
                'total': round(float(currency.totalvalue),2),
                'boolreceive': boolreceive,
            })
        })
    else:
        currency = Crypto.objects.get(name=data['name'])
        currency.price = getPrice(data['name'])
        currency.totalvalue = float(currency.price) * float(currency.quantity)
        currency.save()
        Group('users').send({
            'text':json.dumps({
                'name': currency.name,
                'quantity': currency.quantity,
                'price': round(float(currency.price),2),
                'total': round(float(currency.totalvalue),2),
                'boolreceive': boolreceive,
            })
        })

def getPrice(name):
    url = urljoin(urlmax, name.lower())
    #For dev we can also use logging instead of print
    print(url)
    content = urlopen(url)
    content = content.read()
    return float(json.loads(content)[0]["price_usd"])
