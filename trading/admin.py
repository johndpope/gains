from django.contrib import admin
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import calls
from account.models import MyUser

# Register your models here.

class CallsAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		try:
			if(obj.id is None):
				query = "SELECT id,email,first_name FROM account_myuser WHERE"
				if(obj.cash_intra):
					query = query + " cash_intra = b'1' OR"
				if(obj.cash_positional):
					query = query + " cash_positional = b'1' OR"
				if(obj.stock_future):
					query = query + " stock_future = b'1' OR"
				if(obj.nifty_future):
					query = query + " nifty_future = b'1' OR"
				if(obj.option_calls_covered):
					query = query + " option_calls_covered = b'1' OR"
				if(obj.option_calls_uncovered):
					query = query + " option_calls_uncovered = b'1' OR"
				if(obj.multi_bagger):
					query = query + " multi_bagger = b'1' OR"
				query = query[:-2]
				query =query + ";"
				result = MyUser.objects.raw(query)
				to_emails = []
				for q in result:
					to_emails.append(q.email)
				subject, from_email = 'Subscription Update', 'bluerunfinancial@gmail.com'
				email_body_context = {'stock_name': obj.stock_name,'trade': obj.trade, 'entry_price_range': obj.entry_price_range,'target': obj.target, 'stop_loss': obj.stop_loss, 'time_frame': obj.time_frame}
				body = loader.render_to_string('trading/callissued.txt', email_body_context)
				msg = EmailMultiAlternatives(subject, body, from_email, to_emails)
				msg.send()	
			else:
				if(obj.achived):
					query = "SELECT id,email,first_name FROM account_myuser WHERE"
					if(obj.cash_intra):
						query = query + " cash_intra = b'1' OR"
					if(obj.cash_positional):
						query = query + " cash_positional = b'1' OR"
					if(obj.stock_future):
						query = query + " stock_future = b'1' OR"
					if(obj.nifty_future):
						query = query + " nifty_future = b'1' OR"
					if(obj.option_calls_covered):
						query = query + " option_calls_covered = b'1' OR"
					if(obj.option_calls_uncovered):
						query = query + " option_calls_uncovered = b'1' OR"
					if(obj.multi_bagger):
						query = query + " multi_bagger = b'1' OR"
					query = query[:-2]
					query =query + ";"
					result = MyUser.objects.raw(query)
					to_emails = []
					for q in result:
						to_emails.append(q.email)
					subject, from_email = 'Subscription Update', 'bluerunfinancial@gmail.com'
					email_body_context = {'stock_name': obj.stock_name,'trade': obj.trade, 'entry_price_range': obj.entry_price_range,'target': obj.target, 'stop_loss': obj.stop_loss, 'time_frame': obj.time_frame}
					body = loader.render_to_string('trading/callachieved.txt', email_body_context)
					msg = EmailMultiAlternatives(subject, body, from_email, to_emails)
					msg.send()

		except ex:
			print(ex)
		obj.save()
				
	
admin.site.register(calls, CallsAdmin)