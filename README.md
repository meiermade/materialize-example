# Materialize Bugs
Project to report bugs to Materialize

## Setup
Install uv
```shell
scoop install uv
```

Install Python
```shell
uv python install 3.13
```

Install dependencies
```shell
uv sync
```

Install Pulumi
```shell
scoop install pulumi
```

## Usage
Deploy Postgres and Materialize
```shell
pulumi up
```

Build dbt models
```shell
dbt build
```

## Setup PyCharm
Create a Postgres database connection for materialize and select the following options.
![database_expert_options.png](etc/database_expert_options.png)
![select_database_expert_options.png](etc/select_database_expert_options.png)
