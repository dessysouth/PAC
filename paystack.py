import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()
sk = os.environ.get('secret_key')

def initiate_payment(email, amount):
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

  if response.status_code != 200:
        # Handle HTTP errors
        print(f"Error: HTTP {response.status_code}")
        return None, None

  payment_data = response.json()

  if "data" not in payment_data:
        # Handle unexpected response structure
        print("Error: Unexpected response structure")
        return None, None
  
  auth_url = payment_data["data"].get("authorization_url")
  reference = payment_data["data"].get("reference")

  if not auth_url or not reference:
        # Handle missing data in response
        print("Error: Missing data in response")
        return None, None
  
  return auth_url, reference



  