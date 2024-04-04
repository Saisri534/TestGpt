import os
from dotenv import load_dotenv

# Load environment variables from token.env
load_dotenv('token.env')

def get_jwt_secret():
    return os.environ.get("CHAINLIT_AUTH_SECRET")

res = get_jwt_secret()
print(res)