"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import unittest
from threading import Lock
from .product import Tea, Coffee


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.num_producers = 0  # the number of producers currently registered in the marketplace
        self.num_consumers = 0  # the number of consumers/carts currently registered in the marketplace
        self.producers_id_lock = Lock()  # lock access to atomic integer num_producers
        self.consumers_id_lock = Lock()  # lock access to atomic integer num_consumers
        self.buffer_removal_lock = Lock()
        self.cart_removal_lock = Lock()
        self.print_lock = Lock()
        self.carts = {}  # a dict<id, cart>, a cart is a list of tuples (buffer_id, product)
        self.producers_buffers = {}  # a dict<id, list>, one buffer for each producer (a buffer is a list of products)

    def get_print_lock(self):
        return self.print_lock

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producers_id_lock:
            prod_id = self.num_producers
            self.producers_buffers[prod_id] = []
            self.num_producers += 1
        return prod_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: int  <--------------- changed this from String to int
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        products = self.producers_buffers[producer_id]
        if len(products) < self.queue_size_per_producer:
            products.append(product)
            return True
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.consumers_id_lock:
            cons_id = self.num_consumers
            self.carts[cons_id] = []
            self.num_consumers += 1
        return cons_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        Returns True or False. If the caller receives False, it should wait and then try again
        """
        # Look for the product in the producers' buffers
        with self.buffer_removal_lock:
            for idx, buffer in self.producers_buffers.items():
                if buffer.count(product) > 0:
                    # Add it to the cart
                    self.carts[cart_id].append((idx, product))
                    # Remove it from the producer's buffer
                    buffer.remove(product)
                    return True
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        # Search for the product in the cart
        with self.cart_removal_lock:
            for (idx, prod) in self.carts[cart_id]:
                if prod == product:
                    # Remove it from the cart
                    self.carts[cart_id].remove((idx, prod))
                    # Add it back to the producer's buffer
                    self.producers_buffers[idx].append(product)
                    break

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        result = []
        # Add each product to return list
        for (idx, prod) in self.carts[cart_id]:
            result.append(prod)

        # Empty this cart
        self.carts[cart_id].clear()

        return result


class TestMarketplace(unittest.TestCase):
    """
    Unit testing for Marketplace functions
    register_producer, publish, new_cart, add_to_cart, remove_from_cart, place_order
    """

    def setUp(self):
        self.max_buffer_size = 8
        self.marketplace = Marketplace(self.max_buffer_size)

        self.tea_product = Tea("Some tea", 10, "A bit lame")
        self.coffee_product = Coffee("Coffee", 10, "5.5", "MEDIUM")

        self.prod_0 = self.marketplace.register_producer()
        self.prod_1 = self.marketplace.register_producer()

        self.cons_0 = self.marketplace.new_cart()
        self.cons_1 = self.marketplace.new_cart()
        self.cons_2 = self.marketplace.new_cart()

    def test_register_producer(self):
        self.assertEqual(self.prod_0, 0)
        self.assertEqual(self.prod_1, 1)
        self.assertEqual(self.marketplace.num_producers, 2)

        self.assertListEqual(self.marketplace.producers_buffers[0], [])
        self.assertTrue(len(self.marketplace.producers_buffers[0]) == 0)

    def test_publish(self):
        # Test adding products to producers lists
        self.assertTrue(self.marketplace.publish(self.prod_0, self.tea_product))
        self.assertTrue(self.marketplace.publish(self.prod_0, self.coffee_product))

        self.assertIn(self.tea_product, self.marketplace.producers_buffers[0])
        self.assertIn(self.coffee_product, self.marketplace.producers_buffers[0])
        self.assertNotIn(self.coffee_product, self.marketplace.producers_buffers[1])

        self.assertTrue(self.marketplace.publish(self.prod_1, self.coffee_product))
        self.assertIn(self.coffee_product, self.marketplace.producers_buffers[1])

        self.assertEqual(len(self.marketplace.producers_buffers[0]), 2)
        self.assertEqual(len(self.marketplace.producers_buffers[1]), 1)

        # Test buffer size doesn't exceed limit
        for i in range(2, self.max_buffer_size):
            self.assertTrue(self.marketplace.publish(self.prod_0, self.tea_product))
        self.assertFalse(self.marketplace.publish(self.prod_0, self.tea_product))

    def test_new_cart(self):
        self.assertEqual(self.cons_0, 0)
        self.assertEqual(self.cons_2, 2)
        self.assertEqual(self.marketplace.num_consumers, 3)

        self.assertListEqual(self.marketplace.carts[0], [])
        self.assertTrue(len(self.marketplace.carts[0]) == 0)

    def test_add_to_cart(self):
        self.marketplace.publish(self.prod_0, self.coffee_product)
        for i in range(1, self.max_buffer_size):
            self.assertTrue(self.marketplace.publish(self.prod_0, self.tea_product))
        self.marketplace.publish(self.prod_1, self.tea_product)
        self.marketplace.publish(self.prod_1, self.coffee_product)

        # Producer 0 has 7xTea and 1xCoffee, Producer 1 has 1xTea and 1xCoffee
        self.assertTrue(self.marketplace.add_to_cart(self.cons_0, self.coffee_product))
        self.assertTrue(self.marketplace.add_to_cart(self.cons_0, self.coffee_product))
        self.assertEqual(len(self.marketplace.carts[0]), 2)
        self.assertEqual(len(self.marketplace.carts[1]), 0)

        # No more coffee available
        self.assertFalse(self.marketplace.add_to_cart(self.cons_0, self.coffee_product))
        self.assertFalse(self.marketplace.add_to_cart(self.cons_1, self.coffee_product))
        self.assertNotIn(self.coffee_product, self.marketplace.producers_buffers[0])
        self.assertNotIn(self.coffee_product, self.marketplace.producers_buffers[1])

    def test_remove_from_cart(self):
        self.marketplace.publish(self.prod_0, self.coffee_product)
        for i in range(1, self.max_buffer_size):
            self.assertTrue(self.marketplace.publish(self.prod_0, self.tea_product))
        self.marketplace.publish(self.prod_1, self.tea_product)
        self.marketplace.publish(self.prod_1, self.coffee_product)

        # Producer 0 has 7xTea and 1xCoffee, Producer 1 has 1xTea and 1xCoffee
        self.assertTrue(self.marketplace.add_to_cart(self.cons_0, self.coffee_product))
        self.assertTrue(self.marketplace.add_to_cart(self.cons_0, self.coffee_product))
        self.assertTrue(self.marketplace.add_to_cart(self.cons_0, self.tea_product))

        self.assertTrue(self.marketplace.add_to_cart(self.cons_1, self.tea_product))
        self.assertTrue(self.marketplace.add_to_cart(self.cons_1, self.tea_product))

        # Consumer 0 has 2xCoffee and 1xTea, Consumer 1 has 2xTea
        self.marketplace.remove_from_cart(self.cons_0, self.coffee_product)
        self.marketplace.remove_from_cart(self.cons_0, self.coffee_product)
        self.assertEqual(len(self.marketplace.carts[0]), 1)

        # Producers received their Coffee back
        self.assertIn(self.coffee_product, self.marketplace.producers_buffers[0])
        self.assertIn(self.coffee_product, self.marketplace.producers_buffers[1])

        self.marketplace.remove_from_cart(self.cons_1, self.tea_product)
        self.marketplace.add_to_cart(self.cons_1, self.coffee_product)
        self.marketplace.add_to_cart(self.cons_1, self.coffee_product)
        self.assertEqual(len(self.marketplace.carts[1]), 3)

    def test_place_order(self):
        self.marketplace.publish(self.prod_0, self.coffee_product)
        self.marketplace.publish(self.prod_1, self.coffee_product)
        self.marketplace.publish(self.prod_1, self.tea_product)
        self.marketplace.publish(self.prod_1, self.tea_product)

        self.marketplace.add_to_cart(self.cons_0, self.tea_product)

        self.marketplace.add_to_cart(self.cons_1, self.tea_product)
        self.marketplace.add_to_cart(self.cons_1, self.coffee_product)
        self.marketplace.add_to_cart(self.cons_1, self.coffee_product)

        # Consumer 0 has 1xTea, Consumer 1 has 1xTea and 2xCoffee
        order_0 = self.marketplace.place_order(self.cons_0)
        self.assertListEqual(order_0, [self.tea_product])

        order_1 = self.marketplace.place_order(self.cons_1)
        self.assertIn(self.tea_product, order_1)
        self.assertIn(self.coffee_product, order_1)
        self.assertEqual(len(order_1), 3)
        self.assertListEqual(self.marketplace.carts[1], [])

        # No one gets their coffee back
        self.assertNotIn(self.coffee_product, self.marketplace.producers_buffers[0])
        self.assertNotIn(self.coffee_product, self.marketplace.producers_buffers[1])
