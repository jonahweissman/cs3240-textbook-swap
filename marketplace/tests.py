import datetime
import requests
from django.test import TestCase
from django.test import Client
from django.db import models
from django.utils import timezone

from marketplace.models import Item, User
from marketplace import models


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
                item_price=i,
                item_posted_date=datetime.datetime.now() + i * datetime.timedelta(i),
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

class BuyerSellerCommunicationTests(TestCase):
    def setUp(self):
        self.client = Client()
        bob = User.objects.create(email='bob@virginia.edu').profile
        self.uuid = 'd3c3cf74-d3c1-4420-8f9a-86d8670bb51d'
        item = Item.objects.create(
            item_name='something else',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob)
        conversation = models.Conversation.objects.create(
            item=item,
            buyer=bob)
        root_message = models.Message.objects.create(
            author=bob,
            text='Hey do you want to buy my book?',
            id=self.uuid,
            conversation=conversation,
            in_response_to=None)

    def test_receive_email(self):
        headers = {
            'HTTP_AUTHORIZATION': 'Basic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN5amc=',
        }
        multipart_formdata = {
            'headers[To]': '8becc54808c611029b55+d3c3cf74-d3c1-4420-8f9a-86d8670bb51d@cloudmailin.net',
            'headers[From]': 'bob bobson <bob@virginia.edu>',
            'reply_plain': 'hi this is my reply',
        }
        response = self.client.post('/email/receive',
                                    multipart_formdata,
                                    **headers)

        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(models.Message.objects.get(pk=self.uuid))
        fake_uuid = self.uuid[:-1] + 'a'
        self.assertEqual(len(models.Message.objects.filter(pk=fake_uuid)), 0)
