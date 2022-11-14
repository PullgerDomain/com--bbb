import os
from rest_framework.test import APITestCase
from django.test import tag

from pullgerDevelopmentFramework import nocode


class Test000NoCode(APITestCase):
    @tag('NoCode')
    def test_no_code(self):
        nocode.executor(self=self, file=__file__)
