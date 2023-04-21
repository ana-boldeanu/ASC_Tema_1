"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock, Semaphore


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
