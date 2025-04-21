# modules/crypto_client.py
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
import json
import os
import discord

# endpoint overview: https://coinmarketcap.com/api/documentation/v1/#section/Endpoint-Overview
class CryptoClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.listings_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.quotes_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        self.metadata_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        self.session = Session()
        self.session.headers.update({
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        })
        # emoji mapping for price changes
        self.up_arrow = "⬆️"
        self.down_arrow = "⬇️"

        self.footer = "De data provided by de CoinMarketCap"

    def fetch_crypto_data(self, text):
        """main entry point for fetching crypto data"""
        try:
            if not text:
                # if user doesn't specify coin, get top coins
                return self.fetch_top_coins()
            else:
                # get user specified coin
                return self.fetch_coin_data(text)
        
        # network errors
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(f"Error fetching data: {e}")
            return self.create_error_embed("Connection Error", 
                "De spirits of de digital realm are silent today. De Zulu cannot reach dem... Try again later.")
        
        # catch-all for unexpected errors
        except Exception as e:
            print(f"Unexpected error: {e}")
            return self.create_error_embed("Error",
                "De Zulu has failed to hona de command and has brought shame upon de tribe.")

    def fetch_top_coins(self):
        """fetch top cryptocurrencies by market cap"""
        # define request parameters
        params = {
            'start': '1',
            'limit': '6', # get top 6
            'convert': 'USD'
        }
        
        # fetch data from api
        response = self.session.get(self.listings_url, params=params)
        json_data = json.loads(response.text)
        
        # parse data
        parsed_data = self.parse_top_coins(json_data)
        
        # create and return embed
        return self.create_top_coins_embed(parsed_data)

    def fetch_coin_data(self, text):
        """fetch data for specific cryptocurrency by name or symbol"""
        # 1. try searching by symbol
        symbol = text.upper()
        symbol_params = {
            'symbol': symbol,
            'convert': 'USD'
        }
        
        # fetch data from api
        response = self.session.get(self.quotes_url, params=symbol_params)
        json_data = json.loads(response.text)
        
        # check if data is available
        if "data" in json_data and json_data["data"]:
            # check if symbol is in data dictionary, return it if so
            if symbol in json_data["data"]:
                # if data is a list, keep first entry
                coin_data = json_data["data"][symbol][0] if isinstance(json_data["data"][symbol], list) else json_data["data"][symbol]
                
                # fetch coin_metadata using coin_id
                coin_metadata = self.fetch_coin_metadata(coin_data["id"])
                
                # parse both coin_data and coin_metadata
                parsed_coin = self.parse_single_coin(coin_data, coin_metadata)
                
                return self.create_single_coin_embed(parsed_coin)

        # 2. try searching by slug
        slug = text.lower().replace(' ', '-')   # convert spaces to hyphens
        slug_params = {
            'slug': slug,
            'convert': 'USD'
        }
        
        # fetch data from api
        response = self.session.get(self.quotes_url, params=slug_params)
        json_data = json.loads(response.text)
        
        # check if data is available
        if "data" in json_data and json_data["data"]:
            # for slug-based search, convert to list and get first item
            coin_id = list(json_data["data"].keys())[0]
            coin_data = json_data["data"][coin_id]
            
            # fetch coin_metadata using coin_id
            coin_metadata = self.fetch_coin_metadata(coin_data["id"])
            
            # parse both coin_data and coin_metadata
            parsed_coin = self.parse_single_coin(coin_data, coin_metadata)
            
            return self.create_single_coin_embed(parsed_coin)
        
        # if coin isn't found, return error embed
        return self.create_error_embed("Coin Not Found", 
            f"De Zulu knows many coins, but '{text}' is not among dem. Perhaps it is called by anudda name, or it is too small for de great spirits to notice.")
       
    def fetch_coin_metadata(self, coin_id):
        """fetch coin_metadata for given coin id"""
        try:
            # define request parameters and fetch data from api
            params = {'id': str(coin_id)}   # api requires id parameter as string
            response = self.session.get(self.metadata_url, params=params)
            
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                print(f"Error fetching coin_metadata: Status {response.status_code}, Response: {response.text}")
                return {"data": {}}

        except Exception as e:
            print(f"Error fetching coin_metadata: {e}")
            return {"data": {}}
        
    def parse_single_coin(self, coin_data, coin_metadata):
        """parse single coin data from api responses"""
        # extract general data
        coin_id = coin_data.get("id", 0)
        name = coin_data.get("name", "Unknown")
        slug = coin_data.get("slug", "").lower()
        symbol = coin_data.get("symbol", "")
        quote = coin_data.get("quote", {}).get("USD", {})
        
        # extract price data
        price = quote.get("price") or 0
        change_1h = quote.get("percent_change_1h") or 0
        change_24h = quote.get("percent_change_24h") or 0
        change_7d = quote.get("percent_change_7d") or 0
        market_cap = quote.get("market_cap") or 0
        volume_24h = quote.get("volume_24h") or 0

        # extract supply data
        circulating = coin_data.get("circulating_supply") or 0
        total_supply = coin_data.get("total_supply") or 0
        max_supply = coin_data.get("max_supply") or 0
        
        # format price changes with arrows
        change_1h_formatted = f"{self.up_arrow if change_1h >= 0 else self.down_arrow} {abs(change_1h):.2f}%"
        change_24h_formatted = f"{self.up_arrow if change_24h >= 0 else self.down_arrow} {abs(change_24h):.2f}%"
        change_7d_formatted = f"{self.up_arrow if change_7d >= 0 else self.down_arrow} {abs(change_7d):.2f}%"
        
        # extract coin metadata
        coin_id_str = str(coin_id)
        logo_url = coin_metadata.get("data", {}).get(coin_id_str, {}).get("logo")
        description = coin_metadata.get("data", {}).get(coin_id_str, {}).get("description")
        
        return {
            "id": coin_id,
            "key": f"{name.lower()}|{symbol.lower()}",
            "name": name,
            "slug": slug,
            "symbol": symbol,
            "price": f"${price:,.2f}",
            "change_1h": change_1h_formatted,
            "change_24h": change_24h_formatted,
            "change_7d": change_7d_formatted,
            "market_cap": f"${market_cap:,.0f}",
            "volume_24h": f"${volume_24h:,.0f}",
            "circulating_supply": f"{circulating:,.0f} {symbol}",
            "total_supply": f"{total_supply:,.0f} {symbol}",
            "max_supply": f"{max_supply:,.0f} {symbol}" if max_supply else "Unlimited",
            "logo_url": logo_url,
            "description": description
        }

    def parse_top_coins(self, coins_data):
        """parse top coin data from api response"""
        parsed_data = []

        # iterate through each coin 
        for coin in coins_data.get("data", []):
            # extract general data
            name = coin.get("name", "Unknown")
            symbol = coin.get("symbol", "")
            quote = coin.get("quote", {}).get("USD", {})
            
            # extract price data
            price = quote.get("price") or 0
            change_1h = quote.get("percent_change_1h") or 0
            change_24h = quote.get("percent_change_24h") or 0
            change_7d = quote.get("percent_change_7d") or 0
            
            # format price changes with arrows
            change_1h_formatted = f"{self.up_arrow if change_1h >= 0 else self.down_arrow} {abs(change_1h):.2f}%"
            change_24h_formatted = f"{self.up_arrow if change_24h >= 0 else self.down_arrow} {abs(change_24h):.2f}%"
            change_7d_formatted = f"{self.up_arrow if change_7d >= 0 else self.down_arrow} {abs(change_7d):.2f}%"
            
            entry = {
                "key": f"{name.lower()}|{symbol.lower()}",
                "name": name,
                "symbol": symbol,
                "price": f"${price:,.2f}",
                "change_1h": change_1h_formatted,
                "change_24h": change_24h_formatted,
                "change_7d": change_7d_formatted,
            }

            parsed_data.append(entry)

        return parsed_data
    
    def create_top_coins_embed(self, coins):
        """create embed for top coins"""
        embed = discord.Embed(
            title="De Top Cryptocurrencies",
            description="De Zulu present de top coins by market cap:",
            color=discord.Color.gold()
        )
        
        # iterate to add each coin to embed
        for coin in coins:
            field_value = (
                f"Price: {coin['price']}\n"
                f"1h: {coin['change_1h']}\n"
                f"24h: {coin['change_24h']}\n"
                f"7d: {coin['change_7d']}"
            )
            
            embed.add_field(
                name=f"{coin['name']} ({coin['symbol']})",
                value=field_value,
                inline=True
            )
        
        embed.set_footer(text=self.footer)
        return embed
    
    def create_single_coin_embed(self, coin):
        """create embed for specific coin"""
        symbol = coin['symbol']
        name = coin['name']
        description = f"De Zulu present de details for {name} ({symbol}):"

        # add description if available
        if coin.get('description'):
            description += f"\n\n{coin['description']}"
        
        # create embed with all details
        embed = discord.Embed(
            title=f"{name} ({symbol})",
            description=description,
            color=discord.Color.blue()
        )
        
        # set thumbnail to coin logo if available
        if coin.get('logo_url'):
            embed.set_thumbnail(url=coin['logo_url'])
        
        # add price stats in first row
        embed.add_field(name="Price", value=coin['price'], inline=True)
        embed.add_field(name="Market Cap", value=coin['market_cap'], inline=True)
        embed.add_field(name="24h Volume", value=coin['volume_24h'], inline=True)
        
        # add change percentages in second row
        embed.add_field(name="1h Change", value=coin['change_1h'], inline=True)
        embed.add_field(name="24h Change", value=coin['change_24h'], inline=True)
        embed.add_field(name="7d Change", value=coin['change_7d'], inline=True)
        
        # add supply information in third row
        embed.add_field(name="Circulating Supply", value=coin['circulating_supply'], inline=True)
        embed.add_field(name="Total Supply", value=coin['total_supply'], inline=True)
        embed.add_field(name="Max Supply", value=coin['max_supply'], inline=True)
        
        embed.set_footer(text=self.footer)
        return embed
        
    def create_error_embed(self, title, message):
        """create error message embed"""
        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color.red()
        )
        return embed