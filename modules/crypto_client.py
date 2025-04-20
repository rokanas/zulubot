from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import json
import os

class CryptoClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.parameters = {
            'start':'1',
            'limit':'5000',
            'convert':'USD'
        }
        self.session = Session()
        self.session.headers.update({
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        })

    def get_crypto_data(self):
        """fetch cryptocurrency data from from coinmarketcap api"""
        try:
            response = self.session.get(self.url, params=self.parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Error fetching data: {e}")
            return None
