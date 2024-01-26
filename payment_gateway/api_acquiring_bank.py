#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
import requests
from payment_gateway.config import load_config
from payment_gateway.transaction_format import TransactionFormat

# ==============================================================
#                          BASE
# ==============================================================


class APIAcquiringBank:
    """ This class handle the call to the API Acquiring Bank
    """
    def __init__(self):
        self.acquiring_bank_api_key = load_config().get("acquiring_bank_api_key")
        self.acquiring_bank_api_url = load_config().get("acquiring_bank_api_url")
        self.acquiring_bank_test_mode = load_config().get("acquiring_bank_test_mode")

    def call_acquiring_bank(self, payment_data: TransactionFormat):
        """ Method to decide whether the mock should be called
            or not accoridng to the config.yml file
        """
        if self.acquiring_bank_test_mode is True:
            return self.call_acquiring_bank_mock(payment_data)
        else:
            return self.call_acquiring_bank_real(payment_data)

    def call_acquiring_bank_real(self, payment_data: TransactionFormat):
        """ Method to call Acquiring Bank API
            the build of api_bank_url variable is only an example
        """
        api_bank_url = self.acquiring_bank_api_url + "&appid=" + self.acquiring_bank_api_url
        response_api_bank = requests.get(api_bank_url, json=payment_data)

        return response_api_bank.json

    def call_acquiring_bank_mock(self, payment_data: TransactionFormat):
        """ Method to mock the call to the acquiring Bank
            Some unsuccesfull results will be returned to simulate an unusccessfull operation
        """
        if payment_data.card_owner[-4:] != 'Fail':
            return {
                "message": "Payment executed succesfully",
                "code": 200
            }
        else:
            return {
                "message": "Error during payment",
                "code": 400
            }
