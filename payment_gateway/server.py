#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from fastapi import FastAPI, HTTPException, status, Query, Body, Depends
from sqlalchemy.orm import Session
from payment_gateway.database import get_db
from payment_gateway.process_payment import ProcessPayment
from payment_gateway.retrieve_payment import RetrievePayment
from payment_gateway.transaction_format import TransactionFormat

# ==============================================================
#                          BASE
# ==============================================================

payment_gateway_app = FastAPI()


@payment_gateway_app.post('/process_payment', status_code=status.HTTP_200_OK)
async def process_payment_route(payment_data: TransactionFormat = Body(...), db: Session = Depends(get_db)):
    try:
        process_payment_instance = ProcessPayment(db)
        result_process_payment = process_payment_instance.submit_payment(payment_data)
        return result_process_payment
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {str(e)}"
        )


@payment_gateway_app.get('/retrieve_payment', status_code=status.HTTP_200_OK)
async def retrieve_payment_route(payment_identifier: int = Query(...), db: Session = Depends(get_db)):
    retrieve_payment_instance = RetrievePayment(db)
    payment_details = retrieve_payment_instance.get_payment(payment_identifier)

    if payment_details is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment_details
