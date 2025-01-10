from django.test import TestCase
from .models import Module

class ModuleModelTest(TestCase):
    def test_module_creation(self):
        module = Module.objects.create(
            module_code='CS101',
            module_name='Introduction to Computer Science',
            module_credit=10  # Test the new field
        )
        self.assertEqual(module.module_credit, 10)
