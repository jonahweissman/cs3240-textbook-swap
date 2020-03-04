import datetime
from django.test import TestCase
from django.test import Client
from django.db import models
from django.utils import timezone

from marketplace.models import Item, User


# Create your tests here.

class DummyTestCase(TestCase):
    def setUp(self):
        x = 1
    
    def test_dummy_test_case(self):
        self.assertEqual(1, 1)

class BasicSearchTest(TestCase):
    def setUp(self):
        client = Client()
        self.item_list = []
        bob = User.objects.create().profile
        for i in range(5)[::-1]:
            self.item_list.insert(0, Item.objects.create(
                item_name=f'item {i}',
                item_price=i,
                item_posted_date=datetime.datetime.now() - i * datetime.timedelta(i),
                item_condition="Like New",
                item_seller_name=bob,
            ))
        self.extra_item = Item.objects.create(
            item_name='something else',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob)


    def test_all_items_present(self):
        response = self.client.get('/search?query=item')
        search_results_list = list(response.context['object_list'])
        self.assertListEqual(
            self.item_list,
            search_results_list)
    
    def test_no_extra_items(self):
        response = self.client.get('/search?query=item')
        search_results_list = list(response.context['object_list'])
        self.assertTrue(self.extra_item not in search_results_list)

class TrigramSearchTest(TestCase):
    def setUp(self):
        client = Client()
        self.item_list = []
        bob = User.objects.create().profile
        self.typo = Item.objects.create(
            item_name='this contains a tpyo',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob,
        )
        onion_spellings = ['the onion', 'the onions', 'the onin']
        self.onions = [Item.objects.create(
            item_name=o,
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob,
        ) for o in onion_spellings]
        self.calc_descr = Item.objects.create(
            item_name='Introduction to Biology',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_description="I sure hate calculus lol",
            item_seller_name=bob,
        )
        self.calc_name = Item.objects.create(
            item_name='Introduction to Calculus',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob,
        )


    def test_typo(self):
        response = self.client.get('/search?query=this%20contains%20a%20typo')
        search_results_list = list(response.context['object_list'])
        self.assertIn(self.typo, search_results_list)

    def test_irrelevant_not_included(self):
        response = self.client.get('/search?query=toast')
        search_results_list = list(response.context['object_list'])
        self.assertNotIn(self.typo, search_results_list)

    def test_mispelling_order(self):
        response = self.client.get('/search?query=onion')
        search_results_list = list(response.context['object_list'])
        self.assertEqual(self.onions, search_results_list)

    def test_field_precendence(self):
        response = self.client.get('/search?query=calculus')
        search_results_list = list(response.context['object_list'])
        self.assertEqual(len(search_results_list), 2)
        self.assertTrue(search_results_list.index(self.calc_name)
                        < search_results_list.index(self.calc_descr))

class HTTPResponseTestCase(TestCase):
    def test_home_status_code(self):
        c = Client()
        response = c.get('/')
        self.assertEquals(response.status_code, 200)

    def test_myLstings_status_code(self):
        c = Client()
        response = c.get('/myListings')
        self.assertEquals(response.status_code, 200)

    def test_addListing_status_code(self):
        c = Client()
        response = c.get('/addListing')
        self.assertEquals(response.status_code, 200)
