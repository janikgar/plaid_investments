Plaid Investments
-----------------

This project is a Flask App for linking investment accounts via Plaid to a local worksheet

## Requirements
* Python 3.12
* Poetry
* Flask
* Sqlite3

### Dev Requirements
* Pytest
* Coverage
* Pook
* Black

## Running
```sh
$ poetry install
$ poetry shell
(plaid-investment-py3.12) $ flask --app plaid_investments init-db
(plaid-investment-py3.12) $ flask --app plaid_investments run
```

To test and get coverage report:
```sh
(plaid-investment-py3.12) $ coverage run -m pytest
(plaid-investment-py3.12) $ coverage html
```