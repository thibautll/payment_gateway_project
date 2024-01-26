#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from sqlalchemy.orm import Session
from payment_gateway.database import PaymentStatus, CardInformation

# ==============================================================
#                          BASE
# ==============================================================


class RetrievePayment:
    """ Class to retrieve payment details
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_payment(self, payment_identifier: int) -> dict:
        """ Return Payment details according to the id provided
            by the merchant.
        """
        payment = self.db_session.query(PaymentStatus).filter_by(id=payment_identifier).first()

        if payment:
            card_information = self.db_session.query(CardInformation).filter_by(id=payment.card_id).first()

            masked_card_number = '*' * (len(card_information.card_number) - 4) + card_information.card_number[-4:]

            return {
                "payment_id": payment.id,
                "status_code": payment.status,
                "message": payment.message,
                "amount": payment.amount,
                "currency": payment.currency,
                "card_owner": card_information.owner_name,
                "card_number": masked_card_number,
                "expiration_date": card_information.expiration_date,
                "ccv": card_information.ccv,
            }
        else:
            return None
