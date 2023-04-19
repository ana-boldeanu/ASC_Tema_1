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
        self.carts = {}  # a list of carts; a cart is a list of tuples (product, buffer_id)
        self.producers_buffers = {}  # a list of buffers, one for each producer (a buffer is a list of products)
        self.producers_semaphores = {}  # a list of semaphores to control access to producers buffers

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.producers_id_lock:
            prod_id = self.num_producers
            self.producers_buffers[prod_id] = []
            self.producers_semaphores[prod_id] = Semaphore(value=self.queue_size_per_producer)
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
        semaphore = self.producers_semaphores[producer_id]
        semaphore.acquire(blocking=False)
        self.producers_buffers[producer_id].append(product)
        semaphore.release()

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
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        # Look for the product in the producers' buffers
        for i in range(len(self.producers_buffers)):
            buffer = self.producers_buffers[i]
            if buffer.contains(product):
                # Add it to the cart
                self.carts[cart_id].append((product, i))
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
        for (prod, buff_idx) in self.carts[cart_id]:
            if prod == product:
                # Remove it from the cart
                self.carts[cart_id].remove((prod, buff_idx))
                # Add it back to the producer's buffer
                self.producers_buffers[buff_idx].append(product)

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        result = []
        # Add each product to return list and remove it from the producer's buffer, releasing its semaphore
        for (prod, buff_idx) in self.carts[cart_id]:
            result.append(prod)
            self.producers_buffers[buff_idx].remove(prod)
            self.producers_semaphores[buff_idx].release()

        # Empty this cart
        self.carts[cart_id].clear()

        return result
