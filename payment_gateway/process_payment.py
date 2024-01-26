#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from payment_gateway.transaction_format import TransactionFormat
from payment_gateway.api_acquiring_bank import APIAcquiringBank
from payment_gateway.database import CardInformation, PaymentStatus

# ==============================================================
#                          BASE
# ==============================================================


class ProcessPayment:
    """ Class to process the payment
    """
    def __init__(self, db_uri='sqlite:///./test.db'):
        self.api_bank = APIAcquiringBank()
        self.engine = create_engine(db_uri, echo=True)
        CardInformation.metadata.create_all(self.engine)
        PaymentStatus.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_session(self):
        """ Context Manager to handle session opening and closing
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error in session: {e}")
            raise
        finally:
            session.close()

    def get_or_create_card_information(self, payment_data: TransactionFormat) -> int:
        """ Method to check if card information exists in database.
            Return the id of the corresponding line in database
        """
        with self.get_session() as session:
            try:
                card_information = session.query(CardInformation).filter_by(
                    owner_name=payment_data.card_owner,
                    card_number=payment_data.card_number,
                    expiration_date=payment_data.expiration_date,
                    ccv=payment_data.ccv
                ).one()
                return card_information.id
            except NoResultFound:
                # if card does not exists, we create it
                card_information = CardInformation(
                    owner_name=payment_data.card_owner,
                    card_number=payment_data.card_number,
                    expiration_date=payment_data.expiration_date,
                    ccv=payment_data.ccv
                )
                session.add(card_information)
                session.flush()
                return card_information.id

    def submit_payment(self, payment_data: TransactionFormat) -> dict:
        """ Get the payment details provided by the merchant and
            - call Acquiring Bank API
            - store result in database
            - return result
        """
        # Call Acquiring Bank API and raise error if any
        response_api_acquiring_bank = self.api_bank.call_acquiring_bank(payment_data)

        # Store result in database
        card_id = self.get_or_create_card_information(payment_data)
        with self.get_session() as session:
            payment_status = PaymentStatus(
                card_id=card_id,
                amount=payment_data.amount,
                currency=payment_data.currency,
                status=str(response_api_acquiring_bank['code']),
                message=response_api_acquiring_bank['message']
            )
            session.add(payment_status)
            session.flush()
            payment_id = payment_status.id
            payment_code = payment_status.status
            payment_message = payment_status.message

        # Return Payment status and information
        result_process_payment = {
            "payment_id": payment_id,
            "status": "payment succesfull" if payment_code == "200" else "payment rejected"
        }
        # Return error message only if payment is unsuccesful
        if payment_code != "200":
            result_process_payment["reason"] = payment_message

        return result_process_payment
