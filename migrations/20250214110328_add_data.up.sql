do $$
    declare
        client_id UUID := gen_random_uuid();
        equity_account_id UUID := gen_random_uuid();
        asset_account_id UUID := gen_random_uuid();
        revenue_account_id UUID := gen_random_uuid();
        expense_account_id UUID := gen_random_uuid();
    begin
        insert into client (id, name)
        values (client_id, 'Andy');

        insert into account (id, client_id, name)
        values (equity_account_id, client_id, 'Equity');

        insert into account (id, client_id, name)
        values (asset_account_id, client_id, 'Asset');

        insert into account (id, client_id, name)
        values (revenue_account_id, client_id, 'Revenue');

        insert into account (id, client_id, name)
        values (expense_account_id, client_id, 'Expense');

        insert into transaction (id, client_id, name, date, from_account_id, to_account_id, amount)
        values
            (gen_random_uuid(), client_id, 'Opening Balance', '2025-01-01', equity_account_id, asset_account_id, 1000),
            (gen_random_uuid(), client_id, 'Rent', '2025-01-01', asset_account_id, expense_account_id, 200),
            (gen_random_uuid(), client_id, 'Paycheck', '2025-01-15', revenue_account_id, asset_account_id, 100),
            (gen_random_uuid(), client_id, 'Paycheck', '2025-01-30', revenue_account_id, asset_account_id, 100),
            (gen_random_uuid(), client_id, 'Rent', '2025-02-01', asset_account_id, expense_account_id, 200),
            (gen_random_uuid(), client_id, 'Paycheck', '2025-02-15', revenue_account_id, asset_account_id, 100),
            (gen_random_uuid(), client_id, 'Paycheck', '2025-02-28', revenue_account_id, asset_account_id, 100);
    end;
$$;
