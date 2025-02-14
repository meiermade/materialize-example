import logging
import time
import sqlalchemy as sa
from uuid import uuid4
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)

POSTGRES_URL = "postgresql://sysadmin:changeit@localhost:5432/app"

engine = sa.create_engine(POSTGRES_URL)

MAX_ITERATIONS = 10000

logging.info("Starting to load data")
with engine.connect() as conn:
    logging.info("Getting client")
    sql_get_client = sa.text("select id from client where name = 'Andy'")
    result = conn.execute(sql_get_client).one()
    logging.info(f"Client: {result}")
    client_id = result[0]

    logging.info("Getting accounts")
    sql_get_asset_account = sa.text("select id from account where name = 'Asset'")
    result = conn.execute(sql_get_asset_account).one()
    asset_account_id = result[0]

    sql_get_revenue_account = sa.text("select id from account where name = 'Revenue'")
    result = conn.execute(sql_get_revenue_account).one()
    revenue_account_id = result[0]

    sql_get_expense_account = sa.text("select id from account where name = 'Expense'")
    result = conn.execute(sql_get_expense_account).one()
    expense_account_id = result[0]

    logging.info("Inserting transactions")
    paycheck_amount = 100
    rent_amount = 200
    i = 0
    start_date = date(2025, 3, 1)
    while i < MAX_ITERATIONS:
        current_date = start_date + timedelta(days=i)
        if current_date.day == 1 or current_date.day == 15:
            paycheck_transaction_id = uuid4()
            current_date_str = current_date.isoformat()
            sql_insert_transaction = sa.text(f"""
            insert into transaction (id, client_id, date, name, from_account_id, to_account_id, amount)
            values ('{paycheck_transaction_id}', '{client_id}', '{current_date_str}', 'Paycheck', '{revenue_account_id}', '{asset_account_id}', {paycheck_amount})
            """)
            logging.info(f"Inserting paycheck transaction: {paycheck_transaction_id}")
            conn.execute(sql_insert_transaction)
            conn.commit()
            time.sleep(1)
        if current_date.day == 2:
            rent_transaction_id = uuid4()
            current_date_str = current_date.isoformat()
            sql_insert_transaction = sa.text(f"""
            insert into transaction (id, client_id, date, name, from_account_id, to_account_id, amount)
            values ('{rent_transaction_id}', '{client_id}', '{current_date_str}', 'Rent', '{asset_account_id}', '{expense_account_id}', {rent_amount})
            """)
            logging.info(f"Inserting rent transaction: {rent_transaction_id}")
            conn.execute(sql_insert_transaction)
            conn.commit()
            time.sleep(1)
        i += 1

logging.info("Done loading data")
