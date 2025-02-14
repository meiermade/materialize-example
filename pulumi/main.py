from pulumi import Config, ResourceOptions, FileArchive
from pulumi_command import Provider as CommandProvider
from pulumi_command.local import Command, CommandArgs
from pulumi_docker import (
    Provider as DockerProvider,
    Network,
    NetworkArgs,
    RemoteImage,
    RemoteImageArgs,
    Container,
    ContainerArgs,
    ContainerPortArgs,
    ContainerNetworksAdvancedArgs,
    ContainerVolumeArgs,
    Volume,
    VolumeArgs
)
from pulumi_postgresql import (
    Provider as PostgresProvider,
    ProviderArgs as PostgresProviderArgs,
    Publication,
    PublicationArgs,
    Role,
    RoleArgs,
    Grant,
    GrantArgs
)
from pulumi_materialize import (
    Provider as MaterializeProvider,
    ProviderArgs as MaterializeProviderArgs,
    Secret,
    SecretArgs,
    ConnectionPostgres,
    ConnectionPostgresArgs,
    ConnectionPostgresUserArgs,
    ConnectionPostgresPasswordArgs,
    SourcePostgres,
    SourcePostgresArgs,
    SourcePostgresPostgresConnectionArgs,
    SourcePostgresTableArgs
)
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent.parent
MIGRATIONS_DIR = ROOT_DIR / "migrations"
DBT_DIR = ROOT_DIR / "dbt"
DBT_MODELS_DIR = DBT_DIR / "models"

postgres_config = Config("postgres")
POSTGRES_USER = postgres_config.require("user")
POSTGRES_PASSWORD = postgres_config.require("password")
POSTGRES_DATABASE = postgres_config.require("database")
POSTGRES_MATERIALIZE_USER = postgres_config.require("materialize_user")
POSTGRES_MATERIALIZE_PASSWORD = postgres_config.require("materialize_password")

materialize_config = Config("materialize")
MATERIALIZE_USER = materialize_config.require("user")
MATERIALIZE_DATABASE = materialize_config.require("database")

docker_provider = DockerProvider("default")
command_provider = CommandProvider("default")

network = Network(
    "materialize_example",
    args=NetworkArgs(name="materialize_example"),
    opts=ResourceOptions(provider=docker_provider)
)

postgres_data_volume = Volume(
    "postgres_data",
    args=VolumeArgs(name="postgres_data"),
    opts=ResourceOptions(provider=docker_provider)
)

postgres_image = RemoteImage(
    "postgres",
    args=RemoteImageArgs(name="bitnami/postgresql:16"),
    opts=ResourceOptions(provider=docker_provider)
)

postgres_container = Container(
    "postgres",
    args=ContainerArgs(
        name="postgres",
        image=postgres_image.image_id,
        envs=[
            f"POSTGRESQL_USERNAME={POSTGRES_USER}",
            f"POSTGRESQL_PASSWORD={POSTGRES_PASSWORD}",
            f"POSTGRESQL_POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
            f"POSTGRESQL_DATABASE={POSTGRES_DATABASE}",
            "POSTGRESQL_WAL_LEVEL=logical"
        ],
        ports=[ContainerPortArgs(internal=5432, external=5432)],
        volumes=[
            ContainerVolumeArgs(
                volume_name=postgres_data_volume.name,
                container_path="/bitnami/postgresql",
            )
        ],
        network_mode="bridge",
        networks_advanced=[
            ContainerNetworksAdvancedArgs(name=network.name)
        ]
    ),
    opts=ResourceOptions(provider=docker_provider)
)

MIGRATE_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DATABASE}?sslmode=disable"
MIGRATIONS_PATH = MIGRATIONS_DIR.as_posix()

migrations_archive = FileArchive(MIGRATIONS_DIR.as_posix())

run_migrations = Command(
    "run_migrations",
    args=CommandArgs(
        create=f"docker run --network materialize_example --rm --volume {MIGRATIONS_PATH}:/migrations migrate/migrate:4 -path /migrations -database {MIGRATE_URL} up",
        triggers=[migrations_archive]
    ),
    opts=ResourceOptions(
        provider=command_provider,
        depends_on=[postgres_container]
    )
)

postgres_provider = PostgresProvider(
    "default",
    args=PostgresProviderArgs(
        host="localhost",
        port=5432,
        sslmode="disable",
        username="postgres",
        password=POSTGRES_PASSWORD
    )
)

materialize_publication = Publication(
    "materialize",
    args=PublicationArgs(
        name="materialize",
        database=POSTGRES_DATABASE,
        tables=["public.client", "public.account", "public.transaction"]
    ),
    opts=ResourceOptions(
        provider=postgres_provider,
        depends_on=[run_migrations]
    )
)

postgres_materialize_user = Role(
    "materialize",
    args=RoleArgs(
        name=POSTGRES_MATERIALIZE_USER,
        password=POSTGRES_MATERIALIZE_PASSWORD,
        replication=True,
        login=True
    ),
    opts=ResourceOptions(
        provider=postgres_provider,
        depends_on=[run_migrations]
    )
)

# grant connect on database app to materialize;
grant_connect = Grant(
    "connect",
    args=GrantArgs(
        privileges=["CONNECT"],
        object_type="database",
        database=POSTGRES_DATABASE,
        role=postgres_materialize_user.name
    ),
    opts=ResourceOptions(provider=postgres_provider)
)

# grant usage on schema app.public to materialize;
grant_usage = Grant(
    "usage",
    args=GrantArgs(
        privileges=["USAGE"],
        object_type="schema",
        database=POSTGRES_DATABASE,
        schema="public",
        role=postgres_materialize_user.name
    ),
    opts=ResourceOptions(provider=postgres_provider)
)

# grant select on table client, account, transaction to materialize;
grant_select = Grant(
    "select",
    args=GrantArgs(
        privileges=["SELECT"],
        object_type="table",
        objects=["client", "account", "transaction"],
        database=POSTGRES_DATABASE,
        schema="public",
        role=postgres_materialize_user.name
    ),
    opts=ResourceOptions(provider=postgres_provider)
)

materialize_image = RemoteImage(
    "materialize",
    args=RemoteImageArgs(name="materialize/materialized:latest"),
    opts=ResourceOptions(provider=docker_provider)
)

materialize_container = Container(
    "materialize",
    args=ContainerArgs(
        name="materialize",
        image=materialize_image.image_id,
        ports=[
            ContainerPortArgs(internal=6875, external=6875),
            ContainerPortArgs(internal=6874, external=6874)
        ],
        network_mode="bridge",
        networks_advanced=[
            ContainerNetworksAdvancedArgs(name=network.name)
        ]
    ),
    opts=ResourceOptions(provider=docker_provider)
)

materialize_provider = MaterializeProvider(
    "default",
    args=MaterializeProviderArgs(
        host="localhost",
        port=6875,
        sslmode="disable",
        username=MATERIALIZE_USER
    )
)

app_postgres_password_secret = Secret(
    "postgres_password",
    args=SecretArgs(value=POSTGRES_MATERIALIZE_PASSWORD),
    opts=ResourceOptions(
        provider=materialize_provider,
        depends_on=[materialize_container]
    )
)

app_postgres_connection = ConnectionPostgres(
    "app_postgres",
    args=ConnectionPostgresArgs(
        host=postgres_container.name,
        port=5432,
        ssl_mode="disable",
        database=POSTGRES_DATABASE,
        user=ConnectionPostgresUserArgs(text=postgres_materialize_user.name),
        password=ConnectionPostgresPasswordArgs(name=app_postgres_password_secret.name),
    ),
    opts=ResourceOptions(provider=materialize_provider)
)

app_postgres_source = SourcePostgres(
    "app_postgres",
    args=SourcePostgresArgs(
        postgres_connection=SourcePostgresPostgresConnectionArgs(name=app_postgres_connection.name),
        publication=materialize_publication.name,
        tables=[
            SourcePostgresTableArgs(upstream_name="transaction"),
            SourcePostgresTableArgs(upstream_name="account"),
            SourcePostgresTableArgs(upstream_name="client")
        ]
    ),
    opts=ResourceOptions(provider=materialize_provider)
)

DBT_PATH = DBT_DIR.as_posix()
DBT_MODELS_PATH = DBT_MODELS_DIR.as_posix()
dbt_models_archive = FileArchive(DBT_MODELS_PATH)

dbt_build = Command(
    "dbt_build",
    args=CommandArgs(
        create="uv run dbt build",
        dir=DBT_PATH,
        triggers=[dbt_models_archive]
    ),
    opts=ResourceOptions(
        provider=command_provider,
        depends_on=[app_postgres_source]
    )
)
