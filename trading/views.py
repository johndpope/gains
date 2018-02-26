import json
import time
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from account.models import *
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from trading.forms import *
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core import serializers

from django.views.generic import TemplateView
from account.forms import Settings_APIForm
from account.models import Trading_Platform, MyUser
import ccxt  # noqa: E402


#from quadriga import QuadrigaClient
# Create your views here.environmental1
@require_GET
@login_required(login_url = 'login')
def dashboard(request , id):
        context = {}
        user = get_object_or_404(MyUser , id = request.user.id)
        context['user'] = user

        for exchange in ['Quadrigacx', 'Quoine', 'Kraken', 'Bitfinex', 'Poloniex', 'Bitmext']:
            try:
                api_credentials = Trading_Platform.objects.get( user = user, trading_platform=exchange)
            except:
                api_credentials = 404

            if exchange == "Quadrigacx" and api_credentials:
                key = api_credentials.api_key
                secret = api_credentials.secret
                clientID = str(api_credentials.client_id)
                noonce = str(int(time.time()))  # A unique integer
                signature = genSignature(key, noonce, secret, clientID)
                # PACKAGE INTO JSON FOR SENDING AS A POST
                values = {'key': key,
                        'nonce': noonce,
                        'signature': signature
                        }
                data = urllib.urlencode(values)
                url = 'https://api.quadrigacx.com/v2/user_transactions'
                req = urllib2.Request(url, data=data)
                response = urllib2.urlopen(req)
                print( json.loads(response.read()))
                context['Quadrigacx_data'] = ccxt.quadrigacx({
                "apiKey": api_credentials.api_key,
                "secret": api_credentials.secret, 'uid': api_credentials.client_id
                })
                context['Quadrigacx_transactions'], context['Quadrigacx_data'] = context['Quadrigacx_data'].privatePostUserTransactions(), dir(context['Quadrigacx_data'])
            elif exchange == "Quoine" and api_credentials!=404:
                from quoine.client import Quoinex
                client = Quoinex(api_credentials.api_key, api_credentials.secret)
                print (client.get_trades())
                context['Quoinex_data'] = ccxt.quoinex({"apiKey": api_credentials.api_key,
                "secret": api_credentials.secret})
                context['Quoinex_transactions'], context['Quoinex_data']  = client.get_trades(), dir(context['Quoinex_data'])
            elif exchange == "Kraken" and api_credentials!=404:
                import pandas as pd
                import krakenex

                import datetime
                import calendar
                import time

                # takes date and returns nix time
                def date_nix(str_date):
                    return calendar.timegm(str_date.timetuple())

                # takes nix time and returns date
                def date_str(nix_time):
                    return datetime.datetime.fromtimestamp(nix_time).strftime('%m, %d, %Y')

                # return formatted TradesHistory request data
                def data(start, end, ofs):
                    req_data = {'type': 'all',
                                'trades': 'true',
                                'start': str(date_nix(start)),
                                'end': str(date_nix(end)),
                                'ofs': str(ofs)
                                }
                    return req_data

                k = krakenex.API(api_credentials.api_key, api_credentials.secret)
                data = []
                count = 0
                for i in range(1,11):
                    start_date = datetime.datetime(2016, i+1, 1)
                    end_date = datetime.datetime(2016, i+2, 29)
                    th = k.query_private('TradesHistory', data(start_date, end_date, 1))
                    time.sleep(.25)
                    print(th)
                    th_error = th['error']
                    if int(th['result']['count'])>0:
                        count += th['result']['count']
                        data.append(pd.DataFrame.from_dict(th['result']['trades']).transpose())

                trades = pd.DataFrame
                trades = pd.concat(data, axis = 0)
                trades = trades.sort_values(columns='time', ascending=True)
                #trades.to_csv('data.csv')
                context['Kraken_data'] = ccxt.kraken({"apiKey": api_credentials.api_key, "secret": api_credentials.secret})
                context['Kraken_transactions'], context['Kraken_data'] = trades, dir(context['Kraken_data'])
            elif exchange == "Bitfinex" and api_credentials!=404:
                context['Bitfinex_data'] = ccxt.bitfinex({"apiKey": api_credentials.api_key,
                "secret": api_credentials.secret})
                context['Bitfinex_transactions'], context['Bitfinex_data'] = context['Bitfinex_data'], dir(context['Bitfinex_data']) #.privatePostMytrades()
            elif exchange == "Poloniex" and api_credentials!=404:
                import poloniex
                import datetime
                import time
                polon = poloniex.Poloniex( str(api_credentials.api_key), str(api_credentials.secret))
                start = time.mktime(datetime.datetime(2018, 1, 1).timetuple())
                end = time.mktime(datetime.datetime.now().timetuple())
                fills = polon.returnTradeHistory('BTC_ETH')
                print (polon.returnBalances())
                print (fills)
                if len(fills) > 0:
                    for key, history in fills.items():
                        underscore_index = key.index("_")
                        currency = key[underscore_index + 1:].upper()
                        base_currency = key[:underscore_index].upper()
                        if currency not in transactions:
                            transactions[currency] = []
                        if base_currency not in transactions:
                            transactions[base_currency] = []
                        for transaction in history:
                            # first the currency that was traded
                            transaction_ts = self._to_timestamp(transaction['date'])
                            amount = Decimal(transaction['amount'])
                            base_amount = amount * Decimal(transaction['rate'])
                            if transaction['type'] == 'buy':
                                fee = Decimal(transaction['fee']) * amount
                                amount -= round(fee, PRECISION)
                            else:
                                fee = Decimal(transaction['fee']) * base_amount
                                base_amount -= round(fee, PRECISION)
                            base_price = self._gdax.getHistoryPrice(base_currency,
                                                                    transaction_ts)
                            total = base_amount * Decimal(base_price)


                            context['Poloniex_data'] = ccxt.poloniex({"apiKey": api_credentials.api_key,
                            "secret": api_credentials.secret})
                            context['Poloniex_transactions'] = context['Poloniex_data'] #.privatePostMytrades()
            elif exchange == "Bitmex" and api_credentials!=404:
                context['Bitmex_data'] = ccxt.bitmex({"apiKey": api_credentials.api_key,
                "secret": api_credentials.secret})
                context['Bitmex_transactions'] = context['Bitmex_data'] #.privatePostMytrades()

        return render(request , 'trading/dashboard.html' , context)


@require_GET
@login_required(login_url = 'login')
def profile(request , id):
    context = {}
    user = get_object_or_404(MyUser , id = request.user.id)
    try:
        platform_api = Trading_Platform.objects.filter(user= request.user.id)
    except:
        platform_api = Trading_Platform()
    context['user'] = user
    context['platform_api'] = platform_api
    return render(request, 'trading/profile.html' , context)

@require_http_methods(['GET' , 'POST'])
@login_required(login_url = 'login')
def editprofile(request , id):
	context ={}
	user = get_object_or_404(MyUser, id = request.user.id)
	# context['user'] = user
	# data = {'first_name':user.first_name, 'last_name':user.last_name, 'phone':user.phone}
	if request.method == 'GET':
		context = { 'f' : EditProfileForm({'first_name': user.first_name,'email' : user.email , 'last_name':user.last_name , 'phone':user.phone})}
		return render(request, 'trading/editprofile.html', context)
	else:
		f = EditProfileForm(request.POST)
		if not f.is_valid():
			return render(request, 'trading/editprofile.html', {'f' : f})
		if user.email != f.data['email']:
			if (MyUser.objects.filter(email = f.data['email']).exists()):
				f.add_error('email','User with this email already exists.')
				return render(request, 'trading/editprofile.html', {'f' : f})
			else:
				user.email = f.data['email']
				user.first_name = f.data['first_name']
				user.last_name = f.data['last_name']
				user.phone = f.data['phone']
				user.confirmed_email = False
				user.save()
				try:
					otp = create_otp(user = user, purpose = 'CE')
					email_body_context = { 'u' : user, 'otp' : otp}
					body = loader.render_to_string('trading/confirmemail_email.txt', email_body_context)
					message = EmailMultiAlternatives("Confirm email", body, "bluerunfinancial@gmail.com", [user.email])
					message.send()
					return render(request , 'trading/confirmemail_email_sent.html' , { 'user': user })
				except ex:
					print(ex)
		else:
			user.first_name = f.data['first_name']
			user.last_name = f.data['last_name']
			user.phone = f.data['phone']
			user.save()

		return render(request, 'trading/profile.html', {'user': user})

def confirm_email(request , id , otp):
	user = get_object_or_404(MyUser, id=id)
	otp_object = get_valid_otp_object(user = user, purpose='CE', otp = otp)
	if not otp_object:
		raise Http404()
	user.confirmed_email = True
	user.save()
	otp_object.delete()
	return redirect(reverse('profile' , kwargs={'id': request.user.id}))

class APISettings(TemplateView):
    template_name = 'trading/settings.html'

    def get_context_data(self, **kwargs):
        context = super(APISettings, self).get_context_data(**kwargs)
        print (kwargs)

        try:
            trader = Trading_Platform.objects.get(user=self.request.user, trading_platform = kwargs['platform'])
            if kwargs['platform'] == trader.trading_platform:
                context['settings_form'] = Settings_APIForm(initial={'api_key': trader.api_key, 'secret': trader.secret, 'trading_platform':trader.trading_platform})
                return context
            return context
        except:
            context['settings_form'] = Settings_APIForm()
            return context

    def post(self, request):
        api_key = request.POST.get('api_key')
        secret = request.POST.get('secret')
        client_id = request.POST.get('client_id')
        trading_platform = request.POST.get('trading_platform')
        user = get_object_or_404(MyUser, email = request.user.email)
        try:
            trader = Trading_Platform.objects.get(user=request.user, trading_platform = trading_platform)
            trader.api_key = api_key
            trader.secret = secret
            if trader.client_id != u'':
                trader.client_id = int(client_id)
            trader.save()
        except:
            if client_id != u'':
                client_id = int(client_id)
            else:
                client_id = 0


            trader = Trading_Platform.objects.create(trading_platform = trading_platform,
                    api_key = api_key,
                    secret = secret,
                    user = user,
                    client_id = client_id)


        return HttpResponseRedirect('/')
