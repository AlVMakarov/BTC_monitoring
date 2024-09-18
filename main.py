import asyncio
import aiohttp

BINANCE_PRICE_URL = 'https://data-api.binance.vision/api/v3/ticker?symbols=["BTCUSDT","ETHBTC","SOLBTC"]&windowSize=5m'
GATEIO_PRICE_URL = 'https://api.gateio.ws/api/v4/spot/tickers?currency_pair='
GATEIO_CURRENCY_PAIRS = ['BTC_USDT','ETH_BTC','XMR_BTC','DOGE_BTC']
HTTP_OK = 200

async def get_btc_price_binance():
    async with aiohttp.ClientSession() as session:
        async with session.get(BINANCE_PRICE_URL) as response:
            if response.status == HTTP_OK:
                    data = await response.json()
                    key_json = []
                    for item in data:
                        d = {}
                        s = item['symbol'] if item['symbol'] == 'BTCUSDT' else item['symbol'][-3:] + item['symbol'][:-3]
                        d['name'] = s + '_binance'
                        d['price'] = 1/float(item['lastPrice']) if item['symbol'] != 'BTCUSDT' else float(item['lastPrice'])
                        d['max_price'] = 1/float(item['highPrice']) if item['symbol'] != 'BTCUSDT' else float(item['highPrice'])
                        d['min_price'] = 1/float(item['lowPrice']) if item['symbol'] != 'BTCUSDT' else float(item['lowPrice'])
                        key_json.append(d)
                    return key_json
            else:
                raise Exception(
                    'Не удалось получить цены BTC от Binance.')

async def fetch_gio(session, url):
    async with session.get(url) as response:
        if response.status == HTTP_OK:
            data = await response.json()
            data = data[0]
            d = {}
            s = "BTCUSDT" if data["currency_pair"] == "BTC_USDT" else data["currency_pair"][-3:] + data["currency_pair"][:-4]
            d['name'] = s + '_gateio'
            d['price'] = 1/float(data["last"]) if data["currency_pair"] != 'BTC_USDT' else float(data["last"])
            d['max_price'] = 1/float(data["high_24h"]) if data["currency_pair"] != 'BTC_USDT' else float(data["high_24h"])
            d['min_price'] = 1/float(data["low_24h"]) if data["currency_pair"] != 'BTC_USDT' else float(data["low_24h"])
            return d
        else:
            raise Exception(
                'Не удалось получить цены BTC от Binance.')

async def get_btc_price_gateio():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_gio(session, GATEIO_PRICE_URL + pair) for pair in GATEIO_CURRENCY_PAIRS]
        prices = await asyncio.gather(*tasks)
        return prices


async def main():
    while True:
        prices_binance = await get_btc_price_binance()
        prices_gateio = await get_btc_price_gateio()
        print("Цены binance")
        for item in prices_binance:
            print(item)
        print("Цены gateio")
        for item in prices_gateio:
            print(item)
        await asyncio.sleep(15)

            

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход из программы...")