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
        Thread.__init__(self, kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs['name']
        self.id = None

    def run(self):
        # Get a card ID from the marketplace
        self.id = self.marketplace.new_cart()

        # Execute add and remove operations
        for operation in self.carts:
            if operation['type'] == 'add':
                found_it = self.marketplace.add_to_cart(self.id, operation['product'])
                if ~found_it:
                    time.sleep(self.retry_wait_time)

            if operation['type'] == 'remove':
                self.marketplace.remove_from_cart(self.id, operation['product'])

