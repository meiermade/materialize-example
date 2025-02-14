{{ config(materialized='view') }}

with accounts as (
    select
        id,
        client_id,
        name
    from {{ source('materialize', 'account') }}
)

, transactions as (
    select
        id,
        from_account_id,
        to_account_id,
        amount
    from  {{ source('materialize', 'transaction') }}
)

, withdrawals as (
    select
        from_account_id as account_id,
        sum(amount) as amount
    from transactions
    group by 1
)

, deposits as (
    select
        to_account_id as account_id,
        sum(amount) as amount
    from transactions
    group by 1
)

, combined as (
    select
        a.id as account_id,
        a.client_id,
        a.name,
        coalesce(d.amount, 0) - coalesce(w.amount, 0) as balance
    from accounts a
    left join deposits d on a.id = d.account_id
    left join withdrawals w on a.id = w.account_id
)

select
    account_id,
    client_id,
    name,
    balance
from combined
