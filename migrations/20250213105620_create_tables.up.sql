begin;

create table client
(
    id uuid primary key,
    name varchar(50) not null
);

alter table client replica identity full;

create table account
(
    id uuid primary key,
    client_id uuid not null references client(id),
    name varchar(50) not null
);

alter table account replica identity full;

create table transaction
(
    id uuid primary key,
    client_id uuid not null references client(id),
    name varchar(100) not null,
    date date not null,
    from_account_id uuid not null references account(id),
    to_account_id uuid not null references account(id),
    amount numeric(20, 2) not null
);

alter table transaction replica identity full;

commit;
