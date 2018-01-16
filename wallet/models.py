from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Exchange(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Wallet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100, null=True)
    ethereum_address = models.CharField(max_length=100, null=True)
    ripple_address = models.CharField(max_length=100, null=True)
    exchange_name = models.ForeignKey(Exchange, related_name='cryptos',on_delete=models.CASCADE, null=True)
    api_key = models.CharField(max_length=100, null=True)
    api_secret = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    def __str__(self):
        return self.name

class Crypto(models.Model):
    name = models.CharField(max_length=30, unique=True)
    wallet = models.ForeignKey(Wallet, related_name='cryptos',on_delete=models.CASCADE, null=True)
    quantity = models.FloatField()
    price = models.FloatField()
    totalvalue = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name
"""
class StateWallet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet = models.ForeignKey(Wallet, related_name='states',on_delete=models.CASCADE)
    def __init__(self):
        return self.name

"""

# First part just adding and listing cryptos
# Price should be change on the front end by api call []
"""
To Do
    1. Connect Wallet and Crypto
        --API import of data [Coinbase, Kraken and Binance]
    2. Creationg of Wallet by -API import- of data [Coinbase, Kraken and Binance]
        --View function to create many crypto at once
    3. Creation of State && Connection to Wallet [Time]
    4. User Account --Wallet--
"""
