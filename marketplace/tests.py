import datetime
from django.test import TestCase
from django.db import models
from django.utils import timezone

# Create your tests here.

class DummyTestCase(TestCase):
    def setUp(self):
        x = 1
    
    def test_dummy_test_case(self):
        self.assertEqual(1, 1)