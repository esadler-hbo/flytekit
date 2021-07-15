import typing
from dataclasses import dataclass

from flytekitplugins.sqlalchemy.executor import SQLAlchemyTaskExecutor

from flytekit import kwtypes
from flytekit.core.base_sql_task import SQLTask
from flytekit.core.context_manager import SerializationSettings
from flytekit.core.python_customized_container_task import PythonCustomizedContainerTask
from flytekit.models.security import Secret
from flytekit.types.schema import FlyteSchema


@dataclass
class SQLAlchemyConfig(object):
    """
    Use this configuration to configure task. String should be standard
    sqlalchemy connector format
    (https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).
    Database can be found:
      - within the container
      - or from a publicly accessible source

    Args:
        uri: default sqlalchemy connector
        connect_args: sqlalchemy kwarg overrides -- ex: host
        secret_connect_args: flyte secrets loaded into sqlalchemy connect args
            -- ex: {"password": {"name": SECRET_NAME, "group": SECRET_GROUP}}
    """

    uri: str
    connect_args: typing.Optional[typing.Dict[str, typing.Any]] = None
    secret_connect_args: typing.Optional[typing.Dict[str, Secret]] = None


class SQLAlchemyTask(PythonCustomizedContainerTask[SQLAlchemyConfig], SQLTask[SQLAlchemyConfig]):
    """
    Makes it possible to run client side SQLAlchemy queries that optionally return a FlyteSchema object

    TODO: How should we use pre-built containers for running portable tasks like this. Should this always be a
          referenced task type?
    """

    _SQLALCHEMY_TASK_TYPE = "sqlalchemy"

    def __init__(
        self,
        name: str,
        query_template: str,
        task_config: SQLAlchemyConfig,
        inputs: typing.Optional[typing.Dict[str, typing.Type]] = None,
        output_schema_type: typing.Optional[typing.Type[FlyteSchema]] = None,
        **kwargs,
    ):
        output_schema = output_schema_type if output_schema_type else FlyteSchema
        outputs = kwtypes(results=output_schema)

        super().__init__(
            name=name,
            task_config=task_config,
            container_image="ghcr.io/flyteorg/flytekit:sqlalchemy-6deb81af74ce8f3768553c188ab35660c717420a",
            executor_type=SQLAlchemyTaskExecutor,
            task_type=self._SQLALCHEMY_TASK_TYPE,
            query_template=query_template,
            inputs=inputs,
            outputs=outputs,
            **kwargs,
        )

    @property
    def output_columns(self) -> typing.Optional[typing.List[str]]:
        c = self.python_interface.outputs["results"].column_names()
        return c if c else None

    def get_custom(self, settings: SerializationSettings) -> typing.Dict[str, typing.Any]:
        return {
            "query_template": self.query_template,
            "uri": self.task_config.uri,
            "connect_args": self.task_config.connect_args or {},
            "secret_connect_args": self.task_config.secret_connect_args,
        }
