# modules/crypto_client.py
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import json
import os

# endpoint overview: https://coinmarketcap.com/api/documentation/v1/#section/Endpoint-Overview

class CryptoClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.parameters = {
            'start':'1',
            'limit':'50',
            'convert':'USD'
        }
        self.session = Session()
        self.session.headers.update({
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        })

    def get_crypto_data(self, text):
        """fetch cryptocurrency data from from coinmarketcap"""
        try:
            # fetch and parse data (by default sorted by market cap)
            response = self.session.get(self.url, params=self.parameters)
            json_data = json.loads(response.text)
            parsed_data = self.parse_data(json_data)
            
            if not text:
                # if no user parameter, return top 5 results (discord character limit)
                parsed_data = parsed_data[:5]
                return f"```json\n{json.dumps(parsed_data, indent=2)}\n```" # convert json to formatted json string
            else:
                # if user has specified coin name or symbol
                for coin in parsed_data:
                    if text.lower() in coin['key']:
                        return f"```json\n{json.dumps(coin, indent=2)}\n```" # convert json to formatted json string
                    
                # coin not found
                return f"De Zulu knows many coins, but '{text}' is not among dem. Perhaps it is called by anudda name, or it is too small for de great spirits to notice."
        
        # network errors
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Error fetching data: {e}")
            return "De spirits of de digital realm are silent today. De Zulu cannot reach dem... Try again later."
        # catch-all for unexpected errors
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "De Zulu has failed to hona de command and has brought shame upon de tribe."
    def parse_data(self, json_data):
        """parse raw data received from coinmarketcap"""
        parsed_data = []

        for coin in json_data.get("data", []):
            name = coin.get("name", "Unknown")
            symbol = coin.get("symbol", "")
            quote = coin.get("quote", {}).get("USD", {})
            
            price = quote.get("price") or 0
            change_1h = quote.get("percent_change_1h") or 0
            change_24h = quote.get("percent_change_24h") or 0
            change_7d = quote.get("percent_change_7d") or 0
            market_cap = quote.get("market_cap") or 0
            volume_24h = quote.get("volume_24h") or 0

            circulating = coin.get("circulating_supply") or 0
            total_supply = coin.get("total_supply") or 0
            max_supply = coin.get("max_supply") or 0
            
            entry = {
                "key": f"{name.lower()}|{symbol.lower()}",
                "name": f"**{name} ({symbol})**",
                "price": f"${price:,.2f}",
                "change_1h": f"{change_1h:+.2f}%",
                "change_24h": f"{change_24h:+.2f}%",
                "change_7d": f"{change_7d:+.2f}%",
                "market_cap": f"${market_cap:,.0f}",
                "volume_24h": f"${volume_24h:,.0f}",
                "circulating_supply": f"{circulating:,.0f} {symbol}",
                "total_supply": f"{total_supply:,.0f} {symbol}",
                "max_supply": f"{max_supply:,.0f} {symbol}"
            }

            parsed_data.append(entry)

        return parsed_data