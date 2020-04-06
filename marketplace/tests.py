import datetime
import requests
from django.test import TestCase, LiveServerTestCase
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

class BuyerSellerCommunicationTests(LiveServerTestCase):
    def setUp(self):
        client = Client()
        bob = User.objects.create(email='jw5av@virginia.edu').profile
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
            'host': '91ccc0b3.proxy.webhookapp.com',
            'connection': 'close',
            'user-agent': 'CloudMailin Server',
            'content-type': 'multipart/form-data; boundary=----cloudmailinboundry',
            'authorization': 'Basic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN5amc=',
            'accept-encoding': 'gzip, compressed',
            'x-request-id': 'c60c1c78-2cbd-40e9-88a7-04114d6b9aa4',
            'x-forwarded-for': '3.93.0.165',
            'x-forwarded-proto': 'https',
            'x-forwarded-port': '443',
            'via': '1.1 vegur',
            'connect-time': '8',
            'x-request-start': '1585952006574',
            'total-route-time': '0',
            'content-length': '4080',
        }
        data = open('marketplace/fixtures/email.raw', 'rb').read()
        response = requests.post(f'{self.live_server_url}/email/receive', headers=headers, data=data)

        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(models.Message.objects.get(pk=self.uuid))
        fake_uuid = self.uuid[:-1] + 'a'
        self.assertEqual(len(models.Message.objects.filter(pk=fake_uuid)), 0)
