#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
import unittest
from unittest.mock import Mock
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


class TestRetrievePayment(unittest.TestCase):
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

    @freeze_time("2024-01-25")
    def test_retrieve_payment_successful(self):
        valid_payment_data = {
            "card_owner": "John Doe",
            "card_number": "4012888888881881",
            "expiration_date": "12/25",
            "ccv": "123",
            "amount": 50,
            "currency": "USD"
        }
        response_process_payment = self.client.post('/process_payment', json=valid_payment_data)
        payment_id = response_process_payment.json()['payment_id']

        response_retrieve_payment = self.client.get(f'/retrieve_payment?payment_identifier={payment_id}')

        self.assertEqual(response_retrieve_payment.status_code, 200)

        retrieved_payment_details = response_retrieve_payment.json()
        self.assertEqual(retrieved_payment_details['payment_id'], payment_id)
        self.assertEqual(retrieved_payment_details['card_number'][:12], '*' * 12)

    def test_retrieve_payment_not_found(self):
        response_retrieve_payment = self.client.get('/retrieve_payment?payment_identifier=999')

        self.assertEqual(response_retrieve_payment.status_code, 404)
        self.assertEqual(response_retrieve_payment.json()['detail'], 'Payment not found')


if __name__ == '__main__':
    unittest.main()
