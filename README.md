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

Install dependencies
```shell
uv sync
```

Install Pulumi
```shell
scoop install pulumi
```

## Usage
Deploy
```shell
pulumi up
```

Tear down
```shell
pulumi destroy
```

## Setup PyCharm
Create a Postgres database connection for materialize and select the following options.
![pycharm_materialize_data_source.jpg](etc/pycharm_materialize_data_source.jpg)
![pycharm_materialize_data_source_expert_options.jpg](etc/pycharm_materialize_data_source_expert_options.jpg)
![pycharm_materialize_data_source_expert_options_select.jpg](etc/pycharm_materialize_data_source_expert_options_select.jpg)
