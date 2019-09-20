import os 

def creatFolder(user_temp):
    if not os.path.exists(user_temp):
        os.mkdir(user_temp)