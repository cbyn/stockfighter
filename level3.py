import requests
import json
import os
from multiprocessing import Process

# ************************************************
# Stockfighter has not been up for me to run this!
# ************************************************


class MarketMaker:

    '''Manages a market-making strategy based on fair value defined
    by the volume-weighted moving average of trade prices'''

    def __init__(self, account, venue, stock, history_length, edge, size):
        self.account = account
        self.venue = venue
        self.stock = stock
        self.history_length = history_length
        self.edge = edge
        self.size = size
        self.api_key = os.environ['STOCKFIGHTER']
        self.url = 'https://api.stockfighter.io/ob/api/venues/{}/stocks/{}/'\
            .format(venue, stock)
        self.open_orders = {}
        self.price_history = []
        self.last_trade_time = ''
        self.position = 0
        self.fair_price = 0

    def place_order(self, price, quantity, direction, order_type):
        '''Place an order on the exchange'''
        payload = json.dumps({"orderType": order_type,
                              "qty": quantity,
                              "price": price,
                              "direction": direction,
                              "account": self.account})
        response = requests.post(
            self.url + 'orders',
            data=payload,
            headers={'X-Starfighter-Authorization': self.api_key})
        payload = json.loads(response.text)
        # Update open orders
        self.open_orders[direction] = payload.get('id', '')

    def get_quote(self):
        '''Get quote from the exchange'''
        response = requests.get(self.url + 'quote')
        return json.loads(response.text)

    def cancel_order(self, order):
        '''Cancel order on the exchange'''
        response = requests.delete(self.url + 'orders/' + order)
        payload = json.loads(response.text)
        direction = payload.get('direction', '')
        multiplier = {'buy': 1, 'sell': -1}.get(direction, 0)
        amount = payload.get('totalFilled', 0)
        # Update position
        self.position += multiplier*amount
        # Remove from open orders
        self.open_orders.pop(direction, None)

    def update_price_history(self):
        '''Add latest quote to price history'''
        quote = self.get_quote()
        price = int(quote.get('last', 0))
        volume = int(quote.get('lastSize', 0))
        time = quote.get('lastTrade', '')
        if price > 0 and volume > 0:
            if time != self.last_trade_time:
                self.last_trade_time = time
                self.price_history.append((price, volume))
                if len(self.price_history) > self.history_length:
                    self.price_history = \
                        self.price_history[-self.history_length:]

    def calculate_fair_price(self):
        '''Calculate volume-weighted average price of last 10 trades'''
        if len(self.price_history) == self.history_length:
            return sum(t[0]*t[1] for t in self.price_history) \
                / sum(t[1] for t in self.price_history)
        return 0

    def make_markets(self):
        '''Run market making strategy'''
        while True:
            # Get fair price
            self.update_price_history()
            fair_price = self.calculate_fair_price()
            # If a fair price was calculated and it has changed significantly
            if fair_price > 0 and abs(fair_price - self.fair_price) > 10:
                self._exectute_cancellations(fair_price)
                self._execute_orders(fair_price)
            self.fair_price = fair_price

    def _exectute_cancellations(self):
        '''Concurrently execute cancellations of open orders'''
        cancel_buy, cancel_sell = None, None
        if 'buy' in self.open_orders:
            cancel_buy = Process(target=self.cancel_order,
                                 args=(self.open_orders['buy'],))
            cancel_buy.start()
        if 'sell' in self.open_orders:
            cancel_sell = Process(target=self.cancel_order,
                                  args=(self.open_orders['sell'],))
            cancel_sell.start()
        if cancel_buy:
            cancel_buy.join()
        if cancel_sell:
            cancel_sell.join()

    def _execute_orders(self, price):
        '''Concurrently execute orders for market making'''
        buy_order = Process(target=self.place_order,
                            args=(price - self.edge,
                                  self.size - self.position,
                                  'buy',
                                  'limit'))
        buy_order.start()
        sell_order = Process(target=self.place_order,
                             args=(price + self.edge,
                                   self.position - self.size,
                                   'sell',
                                   'limit'))
        sell_order.start()
        buy_order.join()
        sell_order.join()


if __name__ == '__main__':
    account = raw_input('Enter account: ')
    venue = raw_input('Enter venue: ')
    stock = raw_input('Enter symbol: ')
    history_length = int(raw_input('Enter history length: '))
    edge = int(raw_input('Enter edge: '))
    size = int(raw_input('Enter size: '))
    market_maker = MarketMaker(account,
                               venue,
                               stock,
                               history_length,
                               edge,
                               size)
    market_maker.make_markets()
