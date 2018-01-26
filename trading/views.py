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
from quoine.client import Quoinex

# Create your views here.
@require_GET
@login_required(login_url = 'login')
def dashboard(request , id):
        context = {}
	user = get_object_or_404(MyUser , id = request.user.id)


        Quadrigacx_API = Trading_Platform.objects.get( user = user, trading_platform="Quadrigacx_API")
        Quoinex_API = Trading_Platform.objects.get( user = user, trading_platform="Quoine_API")
        	#Quadrigacx_client = apis.get('Quadrigacx_API')
        	#Quoinex_client = apis'Quoine_API')
        # get market depth
        #depth = client.get_order_book(product_id=products[0]['id'])

        ## place market buy order
        #order = client.create_market_buy( environmental1
            #product_id=products[0]['id'],
            #quantity='100',
            #price_range='0.01')

            # get list of filled orders environmental1
        #filled_orders = client.get_orders(status=client.STATUS_FILLED)
        #except:
            #pass
        #
        Quadrigacx_client = Quoinex(Quadrigacx_API.api_key, Quadrigacx_API.secret)
        Quoine_client = Quoinex(Quoinex_API.api_key, Quoinex_API.secret)
        #print Quadrigacx_API.secret
        #print Quoinex_API.api_key

        try:

        # get products
            Quadrigacx_products = Quadrigacx_client.get_trading_accounts()
            Quinine_products = Quadrigacx_client.get_trading_accounts()
        except QuoineAPIException as e:
            print(e.status_code)
            print(e.messages)




	context['user'] = user
	context['Quadrigacx_products'] = Quadrigacx_products
	context['Quinine_products'] = Quinine_products

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

        try:
            trader = Trading_Platform.objects.get(user=self.request.user)
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
        trading_platform = request.POST.get('trading_platform')
        user = get_object_or_404(MyUser, email = request.user.email)
        try:
            trader = Trading_Platform.objects.get(user=request.user, trading_platform = trading_platform)
            trader.api_key = api_key
            trader.secret = secret
            trader.save()
        except:
            trader = Trading_Platform.objects.create(trading_platform = trading_platform,
                    api_key = api_key,
                    secret = secret,
                    user = user)


        return HttpResponseRedirect('/')
