import os

from dotenv import load_dotenv
from pathlib import Path
env_path = Path('/home/vkondratev/anti_fraud/check/') / '.env'
load_dotenv(dotenv_path=env_path)

class Con_vert():
        host1=os.getenv('host_v'),
        port1=os.getenv('port_v'),
        user1=os.getenv('user_v'),
        password=os.getenv('password_v')
        host=host1[0]
        port=port1[0]
        user=user1[0]
     