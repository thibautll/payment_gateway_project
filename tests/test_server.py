#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from payment_gateway.server import payment_gateway_app
from freezegun import freeze_time

# ==============================================================
#                          BASE
# ==============================================================

payment_client = TestClient(payment_gateway_app)


@freeze_time("2024-01-25")
@patch('payment_gateway.process_payment.ProcessPayment.get_session')
def test_process_payment_ok(mock_get_session):
    """ Validate the possibility to process a succesfull payment
    """
    # Mocking the session
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session

    valid_payment_data = {
        "card_owner": "Martin Dupont",
        "card_number": "8142740445497749",
        "expiration_date": "03/25",
        "ccv": "123",
        "amount": 25,
        "currency": "USD"
    }
    response_process_payment = payment_client.post('/process_payment', json=valid_payment_data)

    assert response_process_payment.status_code == 200
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()
    assert result_process_payment["status"] == "payment succesfull"


@freeze_time("2024-01-25")
@patch('payment_gateway.process_payment.ProcessPayment.get_session')
def test_process_payment_nok(mock_get_session):
    """ Validate the possibility to process a succesfull payment
    """
    # Mocking the session
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session

    valid_payment_data = {
        "card_owner": "Martin Fail",
        "card_number": "4012888888881881",
        "expiration_date": "03/25",
        "ccv": "123",
        "amount": 25,
        "currency": "USD"
    }
    response_process_payment = payment_client.post('/process_payment', json=valid_payment_data)

    assert response_process_payment.status_code == 200
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()
    assert result_process_payment["status"] == "payment rejected"
    assert result_process_payment["reason"] == "Error during payment"


@freeze_time("2024-01-25")
def test_process_payment_invalid_name():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid card owner name format. Use 'Firstname Lastname' format."


@freeze_time("2024-01-25")
def test_process_payment_invalid_card():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid credit card number format."


@freeze_time("2024-01-25")
def test_process_payment_invalid_date():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid date format. Use MM/YY format."


@freeze_time("2024-01-25")
def test_process_payment_past_date():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Expiration date must be greater than the current date."


@freeze_time("2024-01-25")
def test_process_payment_invalid_ccv():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid CCV format. Use a three-digit number."


@freeze_time("2024-01-25")
def test_process_payment_invalid_amount():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid amount. The amount must be greater than 0."


@freeze_time("2024-01-25")
def test_process_payment_invalid_currency():
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
    response_process_payment = payment_client.post('/process_payment', json=invalid_payment_data)

    assert response_process_payment.status_code == 422
    assert response_process_payment.headers["content-type"] == "application/json"

    result_process_payment = response_process_payment.json()

    assert result_process_payment['detail'][0]['msg'] == "Invalid currency format. Use a three-letter code."
