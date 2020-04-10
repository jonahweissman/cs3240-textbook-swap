import datetime
import os
from django.test import TestCase
from django.test import Client
from django.db import models
from django.utils import timezone
from django.core import mail
import requests

from marketplace.models import Item, User
from marketplace import models


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
        for i in range(5):
            self.item_list.insert(0, Item.objects.create(
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
        search_results_list = list(response.context['object_list'])
        self.assertListEqual(
            self.item_list,
            search_results_list)
    
    def test_no_extra_items(self):
        response = self.client.get('/search?query=item')
        search_results_list = list(response.context['object_list'])
        self.assertTrue(self.extra_item not in search_results_list)

    def test_sort_by_price(self):
        response = self.client.get('/search?query=item&sort=price')
        search_results_list = list(response.context['object_list'])
        self.assertListEqual(
            self.item_list,
            search_results_list[::-1])


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


class TestApi(TestCase):
    def test_API_status_code(self):
        item_isbn = "9781985086593"
        apiResponse = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:'+ item_isbn)
        self.assertEquals(apiResponse.status_code, 200)
    
    def testResults(self):
        item_isbn = "9781985086593"
        info_from_api = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn:'+ item_isbn).json()
        item_name= info_from_api['items'][0]['volumeInfo']['title']
        item_author = info_from_api['items'][0]['volumeInfo']['authors'][0]
        self.assertEquals(item_name, "Operating Systems")
        self.assertEquals(item_author, "Remzi H. Arpaci-Dusseau")


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
                'item_edition': 2,
                'item_course': 'CS 9999',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good',
                'item_description': 'Great for learning how to test'
            })
        
        self.assertEquals(len(Item.objects.all()), 1)
        item = Item.objects.all()[0]
        self.assertEquals(item.item_isbn,'9780672327988' )
        self.assertEquals(item.item_edition, 2 )
        self.assertEquals(item.item_course,'CS 9999' )
        self.assertEquals(item.item_price, 10 )
        self.assertEquals(item.item_condition, "Good" )
        self.assertEquals(item.item_name,'Software Testing' )
        self.assertEquals(item.item_author, 'Ron Patton')
        self.assertEquals(item.item_description, 'Great for learning how to test')

    def testAddWithTitleAuthorEdition(self):

        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_name': 'Software Testing',
                'item_author': 'Ron Patton',
                'item_edition': 2,
                'item_course': 'CS 9999',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good',
                'item_description': 'Great for learning how to test'
            })
        
        self.assertEquals(len(Item.objects.all()), 1)
        item = Item.objects.all()[0]
        self.assertEquals(item.item_isbn,'defaultName' )
        self.assertEquals(item.item_edition, 2 )
        self.assertEquals(item.item_course,'CS 9999' )
        self.assertEquals(item.item_price, 10 )
        self.assertEquals(item.item_condition, "Good" )
        self.assertEquals(item.item_name,'Software Testing' )
        self.assertEquals(item.item_author, 'Ron Patton')
        self.assertEquals(item.item_description, 'Great for learning how to test')

    def testAddWithISBN_NoDesc(self):

        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_isbn': '978-0672327988',
                'item_edition': 2,
                'item_course': 'CS 9999',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good'
            })
        self.assertEquals(len(Item.objects.all()), 1)
        item = Item.objects.all()[0]
        self.assertEquals(item.item_isbn,'9780672327988' )
        self.assertEquals(item.item_edition, 2 )
        self.assertEquals(item.item_course,'CS 9999' )
        self.assertEquals(item.item_price, 10 )
        self.assertEquals(item.item_condition, "Good" )
        self.assertEquals(item.item_name,'Software Testing' )
        self.assertEquals(item.item_author, 'Ron Patton')
        description = item.item_description
        self.assertTrue("Software Testing, Second Edition provides practical insight" in description)

    def testAddWithTitleAuthorEdition(self):

        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_name': 'Software Testing',
                'item_author': 'Ron Patton',
                'item_edition': 2,
                'item_course': 'CS 9999',
                'item_image': f,
                'item_price': 10,
                'item_condition': 'Good',
            })
                
        self.assertEquals(len(Item.objects.all()), 1)
        item = Item.objects.all()[0]
        self.assertEquals(item.item_isbn,'defaultName' )
        self.assertEquals(item.item_edition, 2 )
        self.assertEquals(item.item_course,'CS 9999' )
        self.assertEquals(item.item_price, 10 )
        self.assertEquals(item.item_condition, "Good" )
        self.assertEquals(item.item_name,'Software Testing' )
        self.assertEquals(item.item_author, 'Ron Patton')
        self.assertEquals(item.item_description, 'No description entered')

class BuyerSellerCommunicationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.bob = User.objects.create(
            email='bob@example.com',
            first_name='bob',
            last_name='bobson',
        ).profile
        self.uuid = 'd3c3cf74-d3c1-4420-8f9a-86d8670bb51d'
        self.item = Item.objects.create(
            item_name='something else',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=self.bob)
        conversation = models.Conversation.objects.create(
            item=self.item,
            buyer=self.bob)
        root_message = models.Message.objects.create(
            author=self.bob,
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
            'headers[From]': 'bob bobson <bob@example.com>',
            'reply_plain': 'hi this is my reply',
        }
        response = self.client.post('/email/receive',
                                    multipart_formdata,
                                    **headers)

        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(models.Message.objects.get(pk=self.uuid))
        fake_uuid = self.uuid[:-1] + 'a'
        self.assertEqual(len(models.Message.objects.filter(pk=fake_uuid)), 0)

    def test_send_email(self):
        self.client.force_login(self.bob.user)
        response = self.client.post('/email/send', {'item':self.item.pk, 'message':'hi'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        subject = f"New message about {self.item.item_name} from bob bobson"
        self.assertEquals(mail.outbox[0].subject, subject)


class FullConversation(TestCase):
    def setUp(self):
        self.client = Client()
        self.bob = User.objects.create(
            email='bob@example.com',
            username='bob',
            first_name='bob',
            last_name='bobson',
        ).profile
        self.joe = User.objects.create(
            email='joe@example.com',
            username='joe',
            first_name='joe',
            last_name='joeson',
        ).profile
        self.uuid = 'd3c3cf74-d3c1-4420-8f9a-86d8670bb51d'
        self.item = Item.objects.create(
            item_name='Introductory Booling',
            item_price=5,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=self.bob)

    def test_conversation(self):
        self.client.force_login(self.joe.user)
        self.client.post('/email/send', {
            'item': self.item.pk,
            'message': 'hey bob, I want to buy your booling textbook, but I wanna pay 4 instead of 5.'
        })
        self.assertEquals(len(models.Conversation.objects.all()), 1)
        conversation = models.Conversation.objects.all()[0]
        self.assertEquals(conversation.item_id, self.item.pk)
        self.assertEquals(conversation.buyer_id, self.joe.pk)
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue(self.item.item_name in mail.outbox[0].subject)
        self.assertEquals(self.bob.user.email, mail.outbox[0].to[0])
        self.assertEquals(len(models.Message.objects.all()), 1)
        intro_message = models.Message.objects.all()[0]
        self.assertTrue(str(intro_message.pk) in mail.outbox[0].reply_to[0])

        multipart_formdata = {
            'headers[To]': f'8becc54808c611029b55+{intro_message.pk}@cloudmailin.net',
            'headers[From]': 'bob bobson <bob@example.com>',
            'reply_plain': "You got urself a deal! Let's meet by the pier when the rooster crows."
        }
        response = self.client.post('/email/receive',
                                    multipart_formdata,
                                    HTTP_AUTHORIZATION='Basic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN5amc=')
        # this will always be true because we notify on every message
        self.assertEquals(len(models.Message.objects.all()), len(mail.outbox))
        self.assertEquals(len(models.Message.objects.all()), 2)
        self.assertEquals(mail.outbox[1].to[0], self.joe.user.email)
        response_message = models.Message.objects.all()[1]
        self.assertEquals(response_message.in_response_to.id, intro_message.id)
