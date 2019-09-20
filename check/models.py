from django.db import models
from django.shortcuts import reverse




class City(models.Model):
    Город= models.CharField(max_length=20,db_index=True)
    Код_Города= models.CharField(max_length=10,db_index=True)
    def __str__(self):
        return '{}'.format(self.Город)


class Detalizacia(models.Model):
    Код_Города= models.CharField(max_length=10,db_index=True)
    Ид_водителя_короткий = models.SlugField(max_length=10,db_index=True)
    Ид_водителя_длинный =models.SlugField(max_length=32,unique=True)
    Текущий_баланс_водителя=models.CharField(max_length=16,db_index=True)
    Начисления_на_баланс_водителя_исключая_пополнения=models.CharField(max_length=16,db_index=True)
    Размер_всех_доплат=models.CharField(max_length=16,db_index=True)
    Размер_всех_доплат_в_потенициальных_фрод=models.CharField(max_length=16,db_index=True)
    Размер_бонусов_только_из_доплат_до_минималки=models.CharField(max_length=16,db_index=True)
    Текущая_сумма_бонус_плана=models.CharField(max_length=16,db_index=True)

    def get_absolute_url(self):
        return  reverse (' name из url',kwargs={'Ид_водителя_длинный':self.Ид_водителя_длинный}) # в шаблоне  html вместо ссылки {{post.get_absolute_url}}

    def __str__(self):
        return '{}'.format(self.Ид_водителя_длинный)

class trip_dan(models.Model):
    Код_Города= models.CharField(max_length=10,db_index=True)
    Подача=models.TimeField(blank=True,null=True)
    Время_заказа=models.TimeField(blank=True,null=True)
    Время_заказа_БО=models.IntegerField(db_index=True,blank=True,null=True)
    Дистанция=models.IntegerField(db_index=True,blank=True,null=True)
    Старт_поездки=models.DateTimeField (auto_now=False,blank=True,null=True)
    Адрес_подачи=models.SlugField(max_length=50,db_index=True)
    Время_окончания_поездки=models.DateTimeField (auto_now=False,blank=True,null=True)
    Конечный_адрес=models.SlugField(max_length=50,db_index=True,blank=True,null=True)
    Промо=models.SlugField(max_length=12,db_index=True,blank=True,null=True)
    Часть_промо=models.SlugField(max_length=12,db_index=True,blank=True,null=True)
    Доплата=models.SlugField(max_length=12,db_index=True,blank=True,null=True)
    Статус_поездки=models.SlugField(max_length=20,db_index=True,null=True)
    ИД_поездки=models.SlugField(max_length=36,db_index=True)
    ИД_клиента=models.SlugField(max_length=36,db_index=True)
    Стасус=models.SlugField(max_length=16,db_index=True,null=True)
    Имя_клиента=models.SlugField(max_length=36,db_index=True,null=True)
    Телефон_клиента=models.SlugField(max_length=50,db_index=True,null=True)
    Почта_клиента=models.SlugField(max_length=36,db_index=True,null=True)
    ИД_водителя=models.SlugField(max_length=36,db_index=True)
    Имя_водителя=models.SlugField(max_length=36,db_index=True,null=True)
    Телефон_водителя=models.SlugField(max_length=50,db_index=True,null=True)
    Почта_водителя=models.SlugField(max_length=36,db_index=True,null=True)
    Промо_водителя=models.SlugField(max_length=36,db_index=True,null=True)
    Статус_р=models.SlugField(max_length=16,db_index=True,null=True)

    def __str__(self):
        return '{}'.format(self.ИД_поездки)

class SQL_SEL(models.Model):
    id_select=models.AutoField(auto_created=True,  serialize=False,primary_key=True, verbose_name='ID')
    sql_name=models.CharField(max_length=30,db_index=True,null=True)
    sql_select=models.TextField(null=True)

    def __str__(self):
        return '{}'.format(self.sql_name)        