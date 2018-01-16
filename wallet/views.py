from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from accounts.models import accountUser as User
from .models import Crypto
import json
# Create your views here.


def home(request):
    cryptos = Crypto.objects.all()
    return render(request, 'home.html', {'cryptos': cryptos})

def create(request):
    if request.method == 'POST':
        form = CryptoForm(request.POST)
        if form.is_valid():
            form.save()
            data = form.clean_data
            if data['ethereumaddress'] != 'null':
                #print statement should be replace by call Function
                #to get the token [crypto]
                print(data['ethereumaddress'])
            if data['rippleaddress'] != 'null':
                #print statement should be replace by call function to
                #get the number of xrp
                print(data['ethereumaddress'])
            return redirect('home')
    else:
        form = CryptoForm()
    return render(request, 'addCrypto')

def createWallet(request):
    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            form.save()
            data = form.clean_data
            if data['ethereumaddress'] != 'null':
                #print statement should be replace by call Function
                #to get the token [crypto]
                print(data['ethereumaddress'])
            if data['rippleaddress'] != 'null':
                #print statement should be replace by call function to
                #get the number of xrp
                print(data['rippleaddress'])
            if data['api_name'] != 'null':
                #print function should be replaced by call function to the
                #specific api_name creation or import
                print(data['rippleaddress'])



"""
    To Do:
        1. Function to add crypto
        2. Real Time update of price depending on selected platform [axios && vue.js or Channel]
        3. Function Of Wallet
        4. Function: Import of crypto from Exchanges -API- [Coinbase, Kraken, Binance]
"""


# A Joke
def get_drugs(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        k = ['John', 'Joseph', 'Johnny', 'Philippe', 'Phil','Malachi', 'Malibu','Makala',
            'Makari', 'Ripple', 'Bitcoin', 'BitcoinCash','BitTorrent', 'Dash', 'Augur',
            'Dogecoin', 'Hedge', 'Aion', 'Cardano', 'RaiBlocks', 'Qtum', 'EOS', 'VeChain',
            '0x', 'Golem', 'Iris', 'Enigma', 'ChainLink', 'Bancor']
        k = [i for i in k if q in i]
        drug_ = []
        for (i,y) in enumerate(k):
            drug_json = {}
            drug_json['id'] = i
            drug_json['label'] = y
            drug_json['value'] = y
            drug_.append(drug_json)
        data = json.dumps(drug_)
    else:
        data = 'failjjj'
    mimetype = 'application/json'
    return HttpResponse(data,mimetype)
