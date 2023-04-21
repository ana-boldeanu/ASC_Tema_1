"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs['name']
        self.cart_id = None

    def run(self):
        # Get a card ID from the marketplace
        self.cart_id = self.marketplace.new_cart()

        # Execute add and remove operations
        for cart in self.carts:
            for operation in cart:
                action = operation['type']
                product = operation['product']
                quantity = operation['quantity']

                if action == 'add':
                    while quantity > 0:
                        found_it = self.marketplace.add_to_cart(self.cart_id, product)
                        if found_it:
                            quantity -= 1
                        else:
                            time.sleep(self.retry_wait_time)

                elif action == 'remove':
                    while quantity > 0:
                        self.marketplace.remove_from_cart(self.cart_id, product)
                        quantity -= 1

        # Place the order
        ordered_products = self.marketplace.place_order(self.cart_id)

        print_lock = self.marketplace.get_print_lock()

        # Print result
        with print_lock:
            for product in ordered_products:
                print("{} bought {}".format(self.name, product))
