#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Sequence, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

# ==============================================================
#                          BASE
# ==============================================================

Base = declarative_base()


class CardInformation(Base):
    """ Class to store Card informations
    """
    __tablename__ = "card_information"

    id = Column(Integer, Sequence('card_id_seq'), primary_key=True, index=True)
    owner_name = Column(String, nullable=False)
    card_number = Column(String, nullable=False)
    expiration_date = Column(String, nullable=False)
    ccv = Column(String, nullable=False)

    # unicity Constraint on the 3 columns
    __table_args__ = (UniqueConstraint('card_number', 'ccv', 'expiration_date', name='_unique_credit_card'),)

    payment = relationship("PaymentStatus", back_populates="card")


class PaymentStatus(Base):
    """ Class to store Transaction informations
    """
    __tablename__ = "payment_status"

    id = Column(Integer, Sequence('status_id_seq'), primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("card_information.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    message = Column(String, nullable=False)

    card = relationship("CardInformation", back_populates="payment")
