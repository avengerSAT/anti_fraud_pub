import os

from dotenv import load_dotenv
from pathlib import Path
env_path = Path('./check/') / '.env'
load_dotenv(dotenv_path=env_path)

class Con_vert():
        host= os.getenv('host')
        port= os.getenv('port')
        user= os.getenv('user')
        password= os.getenv('password')
