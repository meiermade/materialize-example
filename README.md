# Materialize Example
Example Materialize project.

## Setup
Install uv
```shell
scoop install uv
```

Install Python
```shell
uv python install 3.13
```

Create virtual environment
```shell
uv venv
```

Install dependencies
```shell
uv sync
```

Activate environment
```shell
./.venv/Scripts/activate
```

Install Pulumi
```shell
scoop install pulumi
```

Deploy
```shell
cd pulumi
pulumi up
```

Setup Metabase at http://localhost:3000
![metabase.jpg](etc/metabase.jpg)
![chart.jpg](etc/chart.jpg)

Run load data script
```shell
uv run load_data.py
```
> Useful to see data updated in Metabase

Tear down
```shell
cd pulumi
pulumi destroy
```

## Setup PyCharm
Create a Postgres database connection for materialize and select the following options.
![pycharm_materialize_data_source.jpg](etc/pycharm_materialize_data_source.jpg)
![pycharm_materialize_data_source_expert_options.jpg](etc/pycharm_materialize_data_source_expert_options.jpg)
![pycharm_materialize_data_source_expert_options_select.jpg](etc/pycharm_materialize_data_source_expert_options_select.jpg)

## Bugs
Currently if specifying tables for the materialize source it always updates despite no changes.
```text
❯ pulumi up
Previewing update (prod)

View in Browser (Ctrl+O): https://app.pulumi.com/ameier38/materialize-example/prod/previews/394bd4ed-0243-413c-bbab-17e876b6d6d8

     Type                                 Name                      Plan       Info
     pulumi:pulumi:Stack                  materialize-example-prod
 ~   └─ materialize:index:SourcePostgres  app_postgres              update     [diff: ~tables]
Resources:
    ~ 1 to update
    16 unchanged

Do you want to perform this update? details
  pulumi:pulumi:Stack: (same)
    [urn=urn:pulumi:prod::materialize-example::pulumi:pulumi:Stack::materialize-example-prod]
    ~ materialize:index/sourcePostgres:SourcePostgres: (update)
        [id=self-hosted:u4]
        [urn=urn:pulumi:prod::materialize-example::materialize:index/sourcePostgres:SourcePostgres::app_postgres]
      ~ tables: [
          ~ [0]: {
                  ~ upstreamName: "transaction" => "transaction"
                }
          ~ [1]: {
                  ~ upstreamName: "account" => "account"
                }
          ~ [2]: {
                  ~ upstreamName: "client" => "client"
                }
        ]

```
