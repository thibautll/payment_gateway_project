#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
import unittest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from payment_gateway.server import payment_gateway_app
from payment_gateway.database import CardInformation, PaymentStatus
from sqlalchemy.orm import Session
from freezegun import freeze_time

# ==============================================================
#                          BASE
# ==============================================================

# Test Configuration for database
TEST_DB_URI = 'sqlite:///:memory:'


class TestProcessPayment(unittest.TestCase):
    def setUp(self):
        # Configure FastAPI application for tests
        self.client = TestClient(payment_gateway_app)
        # Create a database for tests
        self.db_session = Session(bind=Mock())
        CardInformation.metadata.create_all(self.db_session.bind)
        PaymentStatus.metadata.create_all(self.db_session.bind)

    def tearDown(self):
        # Clean database after each test
        CardInformation.metadata.drop_all(self.db_session.bind)
        PaymentStatus.metadata.drop_all(self.db_session.bind)
        self.db_session.close()

    @patch('payment_gateway.api_acquiring_bank.APIAcquiringBank.call_acquiring_bank')
    @freeze_time("2024-01-25")
    def test_process_payment_successful(self, mock_call_acquiring_bank):
        valid_payment_data = {
            "card_owner": "John Doe",
            "card_number": "4012888888881881",
            "expiration_date": "12/25",
            "ccv": "123",
            "amount": 50,
            "currency": "USD"
        }
        # Mock configuration to simulate a successful call
        mock_call_acquiring_bank.return_value = {'code': '200', 'message': 'Payment successful'}

        response = self.client.post('/process_payment', json=valid_payment_data)

        self.assertEqual(response.status_code, 200)

        result_process_payment = response.json()
        self.assertEqual(result_process_payment['status'], 'payment successful')

    @patch('payment_gateway.api_acquiring_bank.APIAcquiringBank.call_acquiring_bank')
    @freeze_time("2024-01-25")
    def test_process_payment_rejected(self, mock_call_acquiring_bank):
        valid_payment_data = {
            "card_owner": "John Doe",
            "card_number": "4012888888881881",
            "expiration_date": "12/25",
            "ccv": "123",
            "amount": 50,
            "currency": "USD"
        }
        # Mock configuration to simulate a rejected call
        mock_call_acquiring_bank.return_value = {'code': '400', 'message': 'Payment rejected'}

        response = self.client.post('/process_payment', json=valid_payment_data)

        self.assertEqual(response.status_code, 200)

        result_process_payment = response.json()
        self.assertEqual(result_process_payment['status'], 'payment rejected')

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_name(self):
        """ Validate the error message for
            invalid name
        """

        invalid_payment_data = {
            "card_owner": "Martin",
            "card_number": "8142740445497749",
            "expiration_date": "03/25",
            "ccv": "123",
            "amount": 25,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid card owner name format. Use 'Firstname Lastname' format."

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_card(self):
        """ Validate the error message for
            invalid card number
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497748",
            "expiration_date": "03/25",
            "ccv": "123",
            "amount": 25,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid credit card number format."

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_date(self):
        """ Validate the error message for
            invalid date format
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497749",
            "expiration_date": "03/2025",
            "ccv": "123",
            "amount": 25,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid date format. Use MM/YY format."

    @freeze_time("2024-01-25")
    def test_process_payment_past_date(self):
        """ Validate the error message for
            date older than today
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497749",
            "expiration_date": "03/22",
            "ccv": "123",
            "amount": 25,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Expiration date must be greater than the current date."

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_ccv(self):
        """ Validate the error message for
            invalid ccv
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497749",
            "expiration_date": "03/25",
            "ccv": "12",
            "amount": 25,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid CCV format. Use a three-digit number."

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_amount(self):
        """ Validate the error message for
            invalid amount
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497749",
            "expiration_date": "03/25",
            "ccv": "123",
            "amount": -3,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid amount. The amount must be greater than 0."

    @freeze_time("2024-01-25")
    def test_process_payment_invalid_currency(self):
        """ Validate the error message for
            invalid amount
        """

        invalid_payment_data = {
            "card_owner": "Martin Dupont",
            "card_number": "8142740445497749",
            "expiration_date": "03/25",
            "ccv": "123",
            "amount": 25,
            "currency": "UD"
        }
        response_process_payment = self.client.post('/process_payment', json=invalid_payment_data)

        assert response_process_payment.status_code == 422
        assert response_process_payment.headers["content-type"] == "application/json"

        result_process_payment = response_process_payment.json()

        assert result_process_payment['detail'][0]['msg'] == "Invalid currency format. Use a three-letter code."


if __name__ == '__main__':
    unittest.main()
