import requests
import json
import os
import sys
import random


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
                              "price": price,
                              "direction": direction,
                              "account": self.account})
        response = requests.post(
            self.url.format(venue, stock) + 'orders',
            data=payload,
            headers={'X-Starfighter-Authorization': self.api_key})
        return response

    def get_quote(self, venue, stock):
        resp = requests.get(self.url.format(venue, stock) + 'quote')
        return json.loads(resp.text)

    def execute_block_purchase(self, venue, stock, size, max_price):
        total_filled = 0
        while total_filled < size:
            quote = self.get_quote(venue, stock)
            ask = int(quote.get('ask', sys.maxint))
            if ask <= max_price:
                quantity = min(size - total_filled,
                               random.randint(size/100, size/50))
                resp = self.place_order(
                    venue,
                    stock,
                    ask,
                    quantity,
                    'buy',
                    'immediate-or-cancel')
                filled = int(resp.json().get('totalFilled'))
                total_filled += filled
                print 'Bought: {}, Total: {}'.format(filled, total_filled)


def main():
    account = raw_input('Enter account: ')
    venue = raw_input('Enter venue: ')
    stock = raw_input('Enter symbol: ')
    size = int(raw_input('Enter size: '))
    max_price = int(raw_input('Enter max price: '))

    exchange = Exchange(account)
    exchange.execute_block_purchase(venue, stock, size, max_price)

if __name__ == '__main__':
    main()
