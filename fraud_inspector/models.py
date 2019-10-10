from django.db import models
from django.shortcuts import reverse


class google_sheet(models.Model):
    city = models.CharField(max_length=36, unique=True, db_index=True)
    launch_region_id = models.CharField(max_length=10)
    city_gspread_key = models.CharField(max_length=150)
    city_bonus_plan_dict=models.CharField(max_length=250)
    def get_absolute_url(self):
        return  reverse('name из url',kwargs={'city':self.city}) # в шаблоне  html вместо ссылки {{post.get_absolute_url}}

    def __str__(self):
        return '{}'.format(self.city)

class FraudOrders(models.Model):
    order_id = models.CharField(max_length=36, unique=True, db_index=True)
    order_date = models.DateTimeField(auto_now=False,blank=True,null=True)
    launch_region_id = models.CharField(max_length=10)
    driver_id = models.CharField(max_length=10)
    customer_id = models.CharField(max_length=36)
    state = models.CharField(max_length=10)
    pattern_name = models.CharField(max_length=200)
    resolution = models.CharField(max_length=12)
    compensation = models.CharField(max_length=36)
    update_date = models.DateTimeField(auto_now=True,blank=True,null=True)

    def get_absolute_url(self):
        return  reverse('name из url',kwargs={'order_id':self.order_id}) # в шаблоне  html вместо ссылки {{post.get_absolute_url}}

    def __str__(self):
        return '{}'.format(self.order_id)