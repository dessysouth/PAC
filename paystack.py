import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()
sk = os.environ.get('secret_key')

def pay (email, amount, sk):
  url = "https://api.paystack.co/transaction/initialize"
  data = {
    "email": email,
    "amount": amount * 100,
  }
  headers = {
    "Authorization": "Bearer " + sk,
    "Content-Type": "application/json"
  }
  response = requests.post(url, json.dumps(data), headers=headers)
  