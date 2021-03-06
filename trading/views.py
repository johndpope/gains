import json
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
        #from rotkelchen.args import app_args
        from rotkelchen.rotkelchen import Rotkelchen
        #args = app_args()
        r = Rotkelchen()
        secrets = {}


        for exchange in ['Quadrigacx', 'Quoine', 'Kraken', 'Bitfinex', 'Poloniex', 'Bitmext']:
            try:
                api_credentials = Trading_Platform.objects.get( user = user, trading_platform=exchange)
            except:
                api_credentials = 404

            if api_credentials != 404:
                secrets[exchange] = api_credentials
        print (secrets)
        r.initialize_exchanges(secrets)
        r.process_history()
        print (r)

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
