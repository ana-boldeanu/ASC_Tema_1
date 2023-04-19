"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.name = kwargs['name']
        self.products_data = kwargs['products']
        self.id = None

    def run(self):
        # Register to the marketplace and get an ID
        self.id = self.marketplace.register_producer()

        # Publish the products
        for data in self.products_data:
            name = data[0]
            quantity = data[1]
            wait_time = data[2]
            for product in self.products:
                if product.name == name:
                    while quantity > 0:
                        published_it = self.marketplace.publish(self.id, product)
                        if published_it:
                            time.sleep(wait_time)
                            quantity -= 1
                        else:
                            time.sleep(self.republish_wait_time)
