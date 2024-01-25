#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from payment_gateway.transaction_format import TransactionFormat

# ==============================================================
#                          BASE
# ==============================================================


class ProcessPayment:
    """ This classe will process the payment
    """

    def submit_payment(self, payment_data: TransactionFormat) -> dict:
        """ Get the payment details provided by the merchant and
            - call Acquiring Bank API
            - store result in database
            - return result
        """
        return {
            "payment_id": 1,
            "status": "accepted"
        }
