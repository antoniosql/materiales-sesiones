import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--delta", action="store_true", help="Ejecutar también los escenarios locales de almacenamiento Delta"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--delta"):
        for item in items:
            if "delta" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="ejecutar con --delta; CI lo exige"))


@pytest.fixture(scope="session")
def spark(request):
    pyspark = pytest.importorskip("pyspark", reason="instala las dependencias de desarrollo: pip install -e '.[dev]'")
    builder = (
        pyspark.sql.SparkSession.builder.master("local[1]")
        .appName("tests-datafwk")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
    )
    if request.config.getoption("--delta"):
        from delta import configure_spark_with_delta_pip

        builder = configure_spark_with_delta_pip(
            builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.databricks.delta.snapshotPartitions", "1")
        )
    sesion = builder.getOrCreate()
    yield sesion
    sesion.stop()
