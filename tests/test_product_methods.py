import unittest

import coupons
import event_tickets
import flights
import membership


class ProductMethodsTests(unittest.TestCase):
    def test_each_product_exports_callable_methods(self):
        for product in (membership, coupons, event_tickets, flights):
            with self.subTest(product=product.__name__):
                self.assertTrue(product.__all__)
                self.assertTrue(all(callable(getattr(product, name)) for name in product.__all__))
