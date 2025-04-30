from dotenv import load_dotenv
import os
import requests

# by default looks for a .env in cwd
load_dotenv()

TINGO_API_KEY = os.getenv("TINGO_API_KEY")

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token ' + TINGO_API_KEY
        }
requestResponse = requests.get("https://api.tiingo.com/api/test",
                                    headers=headers)
print(requestResponse.json())