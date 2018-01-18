from django.db import models

# Create your models here.
class calls(models.Model):
	trade_option = (
		('BUY' , 'BUY'),
		('SELL' , 'SELL'),
	)
	created_on = models.DateTimeField(auto_now_add = True)
	stock_name = models.CharField(max_length = 100)
	trade = models.CharField(max_length =4 , choices = trade_option , default = 'BUY')
	entry_price_range = models.CharField(max_length = 50)
	target = models.IntegerField()
	stop_loss = models.IntegerField()
	time_frame = models.CharField(max_length = 100 , blank = True , default = '1 Day')
	comment = models.CharField(max_length = 500 , blank = True , null = True)
	cash_intra = models.BooleanField(default = False)
	cash_positional = models.BooleanField(default = False)
	stock_future = models.BooleanField(default = False)
	nifty_future = models.BooleanField(default = False)
	option_calls_covered = models.BooleanField(default = False)
	option_calls_uncovered = models.BooleanField(default = False)
	multi_bagger = models.BooleanField(default = False)
	achived = models.BooleanField(default = False)
	

	def __str__(self):
		return self.stock_name

	class Meta:
		verbose_name_plural = "calls"