#!/usr/bin/env python
# coding: utf-8

# ==============================================================
#                         IMPORTS
# ==============================================================
from fastapi import FastAPI, HTTPException, status, Query, Body
from payment_gateway.process_payment import ProcessPayment
from payment_gateway.transaction_format import TransactionFormat

# ==============================================================
#                          BASE
# ==============================================================

payment_gateway_app = FastAPI()

process_payment = ProcessPayment()


@payment_gateway_app.post('/process_payment', status_code=status.HTTP_200_OK)
async def process_payment_route(payment_data: TransactionFormat = Body(...)):
    try:
        result_process_payment = process_payment.submit_payment(payment_data)
        return result_process_payment
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameters: {str(e)}"
        )


@payment_gateway_app.get('/retrieve_payment', status_code=status.HTTP_200_OK)
async def retrieve_payment_route(payment_identifier: int = Query(...)):
    # result_add_promocode = promocode_interface.add_promocode(promocode)
    # return {"message": result_process_payment["message"]}
    return {"message": "Payment details"}
