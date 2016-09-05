import requests
import json
import os


class Exchange:

    def __init__(self, account):
        self.account = account
        self.api_key = os.environ['STOCKFIGHTER']
        self.url = 'https://api.stockfighter.io/ob/api/venues/{}/stocks/{}/'

    def place_order(
            self,
            venue,
            stock,
            price,
            quantity,
            direction,
            order_type):
        payload = json.dumps({"orderType": order_type,
                              "qty": quantity,
                              "direction": direction,
                              "account": self.account})
        response = requests.post(
            self.url.format(venue, stock) + 'orders',
            data=payload,
            headers={'X-Starfighter-Authorization': self.api_key})
        return response


def main():
    account = raw_input('Enter account: ')
    venue = raw_input('Enter venue: ')
    stock = raw_input('Enter symbol: ')

    exchange = Exchange(account)
    print exchange.place_order(venue, stock, 0, 100, 'buy', 'market').text

if __name__ == '__main__':
    main()
