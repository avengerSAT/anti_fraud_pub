import csv,sys,os
from check.models import *





def del_dan(p):
    odj=p
    odj.objects.all().delete()


