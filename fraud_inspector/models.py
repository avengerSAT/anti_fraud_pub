from django.db import models
from django.shortcuts import reverse


class FraudOrders(models.Model):
    order_id = models.CharField(max_length=32, unique=True, db_index=True),
    order_date = models.DateTimeField(auto_now=False,blank=True,null=True),
    launch_region_id = models.CharField(max_length=10),
    driver_id = models.CharField(max_length=10),
    customer_id = models.CharField(max_length=32),
    state = models.CharField(max_length=10),
    pattern_id = models.CharField(max_length=3),
    resolution = models.CharField(max_length=12),
    compensation = models.CharField(max_length=32),
    update_date = models.DateTimeField(auto_now=True,blank=True,null=True)

    def get_absolute_url(self):
        return  reverse('name из url',kwargs={'order_id':self.order_id}) # в шаблоне  html вместо ссылки {{post.get_absolute_url}}

    def __str__(self):
        return '{}'.format(self.order_id)