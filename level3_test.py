import unittest

from level3 import MarketMaker


class MarketMakerTest(unittest.TestCase):
    def setUp(self):
        self.mm = MarketMaker('account', 'venue', 'stock', 3, 1, 1)

    def test_first_price_update(self):
        self.mm.update_price_history({'last': 100,
                                      'lastSize': 50,
                                      'lastTrade': '10:00:01'})
        self.assertEqual('10:00:01', self.mm.last_trade_time)
        self.assertEqual([(100, 50)], self.mm.price_history)

    def test_same_quote_not_added_again(self):
        self.mm.update_price_history({'last': 100,
                                      'lastSize': 50,
                                      'lastTrade': '10:00:01'})
        self.mm.update_price_history({'last': 100,
                                      'lastSize': 50,
                                      'lastTrade': '10:00:01'})
        self.assertEqual('10:00:01', self.mm.last_trade_time)
        self.assertEqual([(100, 50)], self.mm.price_history)

    def test_multiple_updates(self):
        self.mm.update_price_history({'last': 100,
                                      'lastSize': 50,
                                      'lastTrade': '10:00:01'})
        self.mm.update_price_history({'last': 105,
                                      'lastSize': 40,
                                      'lastTrade': '10:00:30'})
        self.mm.update_price_history({'last': 103,
                                      'lastSize': 30,
                                      'lastTrade': '10:00:45'})
        self.assertEqual('10:00:45', self.mm.last_trade_time)
        self.assertEqual([(100, 50),
                          (105, 40),
                          (103, 30)], self.mm.price_history)
        self.mm.update_price_history({'last': 100,
                                      'lastSize': 60,
                                      'lastTrade': '10:01:00'})
        self.assertEqual([(105, 40),
                          (103, 30),
                          (100, 60)], self.mm.price_history)

    def test_fair_price(self):
        self.mm.price_history = [(105, 40), (103, 30)]
        self.assertEqual(0, self.mm.get_fair_price())
        self.mm.price_history = [(105, 40), (103, 30), (100, 60)]
        self.assertEqual(102, self.mm.get_fair_price())

if __name__ == '__main__':
    unittest.main()
