from django.test import TestCase
from .pix import *

class PixTestCase(TestCase):
    def test_valid_CPF_no_format(self):
        key = '13668474745'
        self.assertEqual(validate_key_CPF(key), (True, '13668474745'))
    
    def test_valid_CPF_with_formatting(self):
        key = '13668474745'
        self.assertEqual(validate_key_CPF(key), (True, '13668474745'))

    def test_invalid_CPF(self):
        key = '13668474744'
        self.assertEqual(validate_key_CPF(key), (False, ''))

    def test_valid_phone_with_formatting(self):
        key = "(21) 90000-0000"
        result = validate_key_phone(key)
        expected = (True, "+5521900000000")
        self.assertEqual(result, expected)
    
    def test_valid_phone_no_formatting(self):
        key = "21900000000"
        result = validate_key_phone(key)
        expected = (True, "+5521900000000")
        self.assertEqual(result, expected)
    
    def test_not_valid_phone_invalid_area_code(self):
        key = "(10) 90000-0000"
        result = validate_key_phone(key)
        expected = (False, "")
        self.assertEqual(result, expected)

    def test_valid_random(self):
        key = "dcta478j-196l-03fm-t6gh-4298er7845m2"
        result = validate_key_random(key)
        expected = (True, key)
        self.assertEqual(result, expected)

    def test_invalid_random(self):
        key = "dcta478j-196l-0fm-t6gh-4298er7845m2"
        result = validate_key_random(key)
        expected = (False, "")
        self.assertEqual(result, expected)
    
    def test_valid_email(self):
        key = "test@example.com"
        result = validate_key_email(key)
        expected = (True, key)
        self.assertEqual(result, expected)
    
    def test_invalid_email_no_at(self):
        key = "testexample.com"
        result = validate_key_email(key)
        expected = (False, "")
        self.assertEqual(result, expected)
    
    def test_invalid_email_incomplete_domain(self):
        key = "test@example"
        result = validate_key_email(key)
        expected = (False, "")
        self.assertEqual(result, expected)
    
    def test_invalid_email_double_dot(self):
        key = "te..st@example.com"
        result = validate_key_email(key)
        expected = (False, "")
        self.assertEqual(result, expected)

    def test_valid_cnpj_formatted(self):
        key = '11.444.777/0001-61'
        result = validate_key_cnpj(key)
        expected = (True, '11444777000161')
        self.assertEqual(result, expected)
    
    def test_valid_cnpj_only_numbers(self):
        key = '11444777000161'
        result = validate_key_cnpj(key)
        expected = (True, '11444777000161')
        self.assertEqual(result, expected)

    def test_validate_key_with_cpf(self):
        key = '13668474745'
        result = validate_key(key)
        expected = (True, '13668474745')
        self.assertEqual(result, expected)

    def test_validate_key_with_phone(self):
        key = '(21) 90000-0000'
        result = validate_key(key)
        expected = (True, '+5521900000000')
        self.assertEqual(result, expected)
    
    def test_validate_key_with_random(self):
        key = "dcta478j-196l-0tfm-t6gh-4298er7845m2"
        result = validate_key(key)
        expected = (True, "dcta478j-196l-0tfm-t6gh-4298er7845m2")
        self.assertEqual(result, expected)
    
    def test_validate_key_with_email(self):
        key = "person@example.com"
        result = validate_key(key)
        expected = (True, 'person@example.com')
        self.assertEqual(result, expected)
    
    def test_validate_key_with_cnpj(self):
        key = "11.444.777/0001-61"
        result = validate_key(key)
        expected = (True, '11444777000161')
        self.assertEqual(result, expected)