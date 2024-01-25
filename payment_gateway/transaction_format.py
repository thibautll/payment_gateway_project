#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
import re
import datetime
from pydantic import BaseModel, Field, validator

# ==============================================================
#                          BASE
# ==============================================================


class TransactionFormat(BaseModel):
    """ This class defines the format of a transaction
        Parameters are validated with the help of validator method of Pydantic
    """
    card_owner: str = Field(..., description="Card Owner name in 'Firstname Lastname' format")
    card_number: str = Field(..., description="Card Number (16 digit format)")
    expiration_date: str = Field(..., description="Expiration date in MM/YY format")
    ccv: str = Field(..., description="CCV (Card Verification Value)")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Transaction currency code")

    @validator("card_owner")
    def validate_card_owner_name(card_owner_name: str) -> str:
        """ Method to validate the card owner name format
            A regex is used to validate that the format is  as 'Firstname Lastname'
        """
        name_regex = re.compile(r"^[A-Za-z]+\s[A-Za-z]+$")

        if not name_regex.match(card_owner_name):
            raise ValueError("Invalid card owner name format. Use 'Firstname Lastname' format.")
        return card_owner_name

    @validator("card_number")
    def validate_credit_card_number(card_number: str) -> str:
        """ Method to validate card number format
            A regex is used to validate that the format is a 16 digit format
            as well as Luhn algorithm is also checked
        """
        def valid_luhn_algorithm(number_card: str) -> str:
            """ Internal method to validate luhn algorithm
            """
            digits = [int(digit) for digit in str(number_card)]
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = 0
            checksum += sum(odd_digits)
            for ed in even_digits:
                checksum += sum([int(d) for d in str(ed*2)])
            return checksum % 10 == 0

        card_number_regex = re.compile(r"^\d{16}$")

        if not valid_luhn_algorithm(card_number) or not card_number_regex.match(card_number):
            raise ValueError("Invalid credit card number format.")

        return card_number

    @validator("expiration_date")
    def validate_expire_date_format(expire_date: str) -> str:
        """ Method to validate that expire date is under the format MM/YY
            and greater than actual date
        """
        date_regex = re.compile(r"^\d{2}/\d{2}$")
        if not date_regex.match(expire_date):
            raise ValueError("Invalid date format. Use MM/YY format.")

        # String is converted as a datetime object to validate the format
        date_expiration = datetime.datetime.strptime(expire_date, "%m/%y")

        # Check that the date is greater than current date
        if date_expiration <= datetime.datetime.now():
            raise ValueError("Expiration date must be greater than the current date.")

        return expire_date

    @validator("ccv")
    def validate_ccv(ccv: str) -> str:
        """ Method to validate that the CCV provided is valid
        """
        ccv_regex = re.compile(r"^\d{3}$")

        if not ccv_regex.match(ccv):
            raise ValueError("Invalid CCV format. Use a three-digit number.")

        return ccv

    @validator("amount")
    def validate_amount(amount: float) -> float:
        """ Method to validate the amount provided by the merchant
            is greater than zero
        """
        if amount <= 0:
            raise ValueError("Invalid amount. The amount must be greater than 0.")
        return amount

    @validator("currency")
    def validate_currency(currency: str) -> str:
        """ Method to validate that the currency provided by the merchant is valid
        """
        currency_regex = re.compile(r"^[A-Za-z]{3}$")

        if not currency_regex.match(currency):
            raise ValueError("Invalid currency format. Use a three-letter code.")
        return currency
