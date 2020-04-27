import datetime
import os
from uuid import UUID
from django.test import TestCase
from django.test import Client
from django.db import models
from django.utils import timezone
from django.core import mail
from django.forms import ValidationError
import requests

from marketplace.models import Item, User
from marketplace import models, forms


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
        response = self.client.get('/search?query=item&sort=date')
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
        onion_spellings = ['The Onion', 'The Onions', 'The Onin']
        self.onions = [Item.objects.create(
            item_name=o,
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob,
        ) for o in onion_spellings]
        self.calc_author = Item.objects.create(
            item_name='Introduction to Biology',
            item_author='Joe Calculus',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_seller_name=bob,
        )
        self.calc_name = Item.objects.create(
            item_name='Introduction to Calculus',
            item_price=1,
            item_posted_date=datetime.datetime.now(),
            item_condition="Like New",
            item_author='Stewart',
            item_isbn=12345,
            item_course='MATH 1234',
            item_seller_name=bob,
        )
        self.java = Item.objects.create(
            item_name='Big Java, Binder Ready Edition (this name is long)',
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
        self.assertEqual(search_results_list[0], self.onions[0])
        self.assertTrue(search_results_list.index(self.onions[0])
                        < search_results_list.index(self.onions[1])
                        < search_results_list.index(self.onions[2]))

    def test_big_length_difference(self):
        response = self.client.get('/search?query=java')
        results = list(response.context['object_list'])
        self.assertIn(self.java, results)

    def test_field_precendence(self):
        response = self.client.get('/search?query=calculus')
        results = list(response.context['object_list'])
        self.assertEqual(len(results), 2)
        self.assertTrue(results.index(self.calc_name)
                        < results.index(self.calc_author))

    def test_isbn(self):
        response = self.client.get('/search?query=12345')
        results = list(response.context['object_list'])
        self.assertIn(self.calc_name, results)
        self.assertEqual(results[0], self.calc_name)

    def test_author(self):
        response = self.client.get('/search?query=Stewart')
        results = list(response.context['object_list'])
        self.assertIn(self.calc_name, results)
        self.assertEqual(results[0], self.calc_name)

    def test_whole_course(self):
        response = self.client.get('/search?query=math%201234')
        results = list(response.context['object_list'])
        self.assertIn(self.calc_name, results)
        self.assertEqual(results[0], self.calc_name)

    def test_partial_course(self):
        response = self.client.get('/search?query=math')
        results = list(response.context['object_list'])
        self.assertIn(self.calc_name, results)
        self.assertEqual(results[0], self.calc_name)

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

    def testBetaBugCase(self):
        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_isbn': '978-0-321-98992-5',
                'item_edition': '5',
                'item_course': 'MATH 3351',
                'item_image': f,
                'item_price': '100',
                'item_condition': 'Good',
                'item_description': 'Loose leaf'
            })
        item = Item.objects.all()[0]
        self.assertEquals(len(Item.objects.all()), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Linear Algebra" in item.item_name)
        self.assertTrue("Loose leaf" in item.item_description)
        self.assertEquals("MATH 3351", item.item_course)

    def testLowerCaseCourse(self):
        with open('marketplace/fixtures/textbook.jpg', 'rb') as f:
            response = self.client.post('/addListing', {
                'item_isbn': '978-0-321-98992-5',
                'item_edition': '5',
                'item_course': 'math 3351',
                'item_image': f,
                'item_price': '100',
                'item_condition': 'Good',
                'item_description': 'Loose leaf'
            })
        item = Item.objects.all()[0]
        self.assertEquals(len(Item.objects.all()), 1)
        self.assertEquals(response.status_code, 200)
        self.assertTrue("Linear Algebra" in item.item_name)
        self.assertTrue("Loose leaf" in item.item_description)
        self.assertEquals("MATH 3351", item.item_course)

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
                'item_condition': 'Good',
                'item_description': ''
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
        self.root_message = models.Message.objects.create(
            author=self.bob,
            text='Hey do you want to buy my book?',
            id=UUID(self.uuid),
            conversation=conversation,
            in_response_to=None)

    def test_unauthorized(self):
        headers = {
            'HTTP_AUTHORIZATION': 'Basic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN4amc=',
        }
        multipart_formdata = {
            'headers[To]': '8becc54808c611029b55+d3c3cf74-d3c1-4420-8f9a-86d8670bb51d@cloudmailin.net',
            'headers[From]': 'bob bobson <bob@example.com>',
            'reply_plain': 'hi this is my reply',
        }
        response = self.client.post('/email/receive',
                                    multipart_formdata,
                                    **headers)

        self.assertEquals(response.status_code, 403)
        headers = {
            'HTTP_AUTHORIZATION': 'BAsic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN4amc=',
        }
        response = self.client.post('/email/receive',
                                    multipart_formdata,
                                    **headers)

        self.assertEquals(response.status_code, 403)
        response = self.client.post('/email/receive',
                                    multipart_formdata)
        self.assertEquals(response.status_code, 403)

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

    def test_receive_email_form(self):
        data = {
            'in_response_to': '8becc54808c611029b55+d3c3cf74-d3c1-4420-8f9a-86d8670bb51d@cloudmailin.net',
            'author': 'bob bobson <bob@example.com>',
            'text': 'hi this is my reply',
        }
        f = forms.ReceiveMessageForm(data)
        valid = f.is_valid()
        if not valid:
            print(f.errors)
        self.assertTrue(valid)
        self.assertEquals(f.cleaned_data['in_response_to'].pk,
                          self.root_message.pk)
        self.assertEquals(f.cleaned_data['author'], self.bob)
        self.assertEquals(f.cleaned_data['text'], data['text'])
        self.assertEquals(f.cleaned_data['conversation'].pk,
                          self.root_message.conversation.pk)

    def test_receive_tricky_email(self):
        headers = {
            'HTTP_AUTHORIZATION': 'Basic Y2xvdWRtYWlsaW46UWd2OWh5RFRCdllkUVdZMlluUm5lOXQ1WTg1ZTV5dHFKcFN5amc=',
        }
        multipart_formdata = {
            'headers[To]': '"8becc54808c611029b55+d3c3cf74-d3c1-4420-8f9a-86d8670bb51d@cloudmailin.net" <8becc54808c611029b55+d3c3cf74-d3c1-4420-8f9a-86d8670bb51d@cloudmailin.net>',
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
        symb = '!@#$%^&*()<>/'
        self.client.post('/email/send', {
            'item': self.item.pk,
            'message': 'hey bob, I want to buy your booling textbook, but I wanna pay 4 instead of 5. Here are my favorite symbols: %s' % symb
        })
        self.assertEquals(len(models.Conversation.objects.all()), 1)
        conversation = models.Conversation.objects.all()[0]
        self.assertEquals(conversation.item_id, self.item.pk)
        self.assertEquals(conversation.buyer_id, self.joe.pk)
        self.assertEquals(len(mail.outbox), 1)
        self.assertTrue(self.item.item_name in mail.outbox[0].subject)
        self.assertEquals(self.bob.user.email, mail.outbox[0].to[0])
        self.assertIn(symb, mail.outbox[0].body)
        self.assertNotIn('<a href', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn('<a href="https://textbookswapuva.herokuapp.com/item/%d/conversation">' % self.item.pk, html)
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
        response = self.client.get(f'/item/{self.item.pk}/conversation')
        form = response.context['conversation_list'][0]['form']
        with self.assertRaises(ValidationError):
            form.fields['text'].clean('')
        form_data = form.initial
        for k, item in form_data.items():
            form_data[k] = item.pk
        form_data['text'] = 'Sorry, running late'
        response = self.client.post(f'/item/{self.item.pk}/conversation', form_data)
        self.assertEquals(len(models.Message.objects.all()), len(mail.outbox))
        self.assertEquals(len(models.Message.objects.all()), 3)
        running_late = models.Message.objects.all()[2]
        self.assertEquals(running_late.in_response_to, response_message)

class IndexTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.item_list = []
        self.bob = User.objects.create().profile
        for i in range(25):
            self.item_list.append(Item.objects.create(
                item_name=f'item {i}',
                item_author=f'author {i}',
                item_edition=i,
                item_course=f'CS {i}{i}{i}{i}',
                item_price=i,
                item_posted_date=datetime.datetime.now() - i * datetime.timedelta(i),
                item_condition="Like New",
                item_seller_name=self.bob,
            ))

    def test_contains_all_items(self):
        response = self.client.get('/')
        items = list(response.context['allItems'])
        self.assertEquals(len(items), len(self.item_list))
        self.assertEquals(items, self.item_list)

    def test_limits_total_items(self):
        new_items = []
        for i in range(25):
            new_items.append(Item.objects.create(
                item_name=f'item {i} pt 2',
                item_author=f'author {i}',
                item_edition=i,
                item_course=f'CS {i}{i}{i}{i}',
                item_price=i,
                item_posted_date=datetime.datetime.now() + (i+1) * datetime.timedelta(i),
                item_condition="Like New",
                item_seller_name=self.bob,
            ))
        new_all_items = sorted(new_items + self.item_list, key=lambda i: i.item_posted_date, reverse=True)
        response = self.client.get('/')
        items = list(response.context['allItems'])
        self.assertEquals(len(items), 30)
        self.assertEquals(items, new_all_items[:30])



class Profile(TestCase):
    def setUp(self):
        User.objects.create().profile

    def test_profile(self):
        Profile = User.objects.last().profile
