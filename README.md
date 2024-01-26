Payment Gateway Project
=================

API based application payment gateway.

Installation
------------

Clone repository:

```
git clone git@github.com:thibautll/payment_gateway_project.git
```

Install dependencies

- System dependencies
```
curl -sSL https://install.python-poetry.org | python3 -
```

- Python dependencies and virtual env activation
```
poetry install
poetry shell
```

Execute the service
------------
```
poetry run uvicorn payment_gateway.server:payment_gateway_app --reload
```

Execute the Tests
------------
```
poetry run pytest tests/test_retrieve_payment.py
poetry run pytest tests/test_process_payment.py
```

Technical Considerations
------------
```
The project is divided as follow in payment_gateway:
- server.py handles all incoming request. It co,tains two routes:
    - process_payment: to process a payment
    - retrieve_payment: to retrieve a payment

- process_payment.py contains the class ProcessPayment.
    - the method submit_payment will be executed when a payment needs to be processed

- retrieve_payment.py contains the class RetrievePayment
    - the method get_payment will be executed when a merchant wants to retrieve payment details

- api_acquiring_bank.py simulates the Acquiring Bank API. A mock is used to simulate it.
    If The ward owner name ends with "Fail", then the result will fail. Otherwise it will succeed.

- database.py: contains all information and configuration related to the database.
    A sqlite databse with SQLAlchemy has been implemented.

- transaction_format.py details the format of a transaction.
    Validations are done on each field to ensure parameters provided by the merchant are correct.

At the root, the file config.yml will details the API Acquiring Bank configuration
