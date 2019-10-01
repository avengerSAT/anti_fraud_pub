import os

from dotenv import load_dotenv
from pathlib import Path
env_path = Path('antifraud/') / '.env'
load_dotenv(dotenv_path=env_path)

class Con_vert():
        host= os.getenv('host_vertica')
        port= os.getenv('port_vertica')
        user= os.getenv('user_vertica')
        password= os.getenv('password_vertica')
        