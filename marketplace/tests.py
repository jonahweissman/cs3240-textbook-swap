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

class SearchTestPagination(TestCase):
    def setUp(self):
        client = Client()
        self.item_list = []
        bob = User.objects.create().profile
        for i in range(5)[::-1]:
            self.item_list.append(Item.objects.create(
                item_name=f'item {i}',
                item_author=f'author {i}',
                item_edition=i,
                item_course=f'CS {i}{i}{i}{i}',
                item_price=i,
                item_posted_date=datetime.datetime.now() + i * datetime.timedelta(i),
                item_condition="Like New",
                item_seller_name=bob,
            ))
        self.extra_item = Item.objects.create(
            item_name='something else',
            item_author="John",
            item_edition=5,
            item_course="APMA 3080",
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob)


    def test_all_items_present(self):
        response = self.client.get('/search?query=item')
        search_results_list = list(response.context['search_results'])
        self.assertListEqual(
            self.item_list,
            search_results_list)
    
    def test_no_extra_items(self):
        response = self.client.get('/search?query=item')
        search_results_list = list(response.context['search_results'])
        self.assertTrue(self.extra_item not in search_results_list)

    def test_sort_by_price(self):
        response = self.client.get('/search?query=item&sort=price')
        search_results_list = list(response.context['search_results'])
        self.assertListEqual(
            self.item_list,
            search_results_list[::-1])

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


class AddListingTests(TestCase):
    def setUp(self):
        some_guy = User.objects.create()
        self.client = Client()
        self.client.force_login(some_guy)


    def testAddNoISBN(self):
        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_name': 'A textbook',
                'item_author': 'some guy',
                'item_edition': '1',
                'item_course': 'ABC 1010',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good',
                'item_description': 'just a book'
            })
        self.assertEquals(len(Item.objects.all()), 1)

    def testEmptyDatabase(self):
        self.assertEquals(len(Item.objects.all()), 0)

    def testAddWithISBN(self):

        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_isbn': '978-0672327988',
                'item_course': 'CS 9999',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good',
                'item_description': 'Great for learning how to test'
            })
        
        #https://isbnsearch.org/isbn/9780672327988

        #print("\n item_author: " + Item.objects.get().getAuthor())
        self.assertEquals(len(Item.objects.all()), 1)
        self.assertEquals(Item.objects.get().getISBN(),'9780672327988' )
        self.assertEquals(Item.objects.get().getTitle(),'Software Testing' )
        self.assertEquals(Item.objects.get().getAuthor(), 'Ron Patton')

