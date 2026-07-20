"""
job_board_pipeline_dag.py

DAG Airflow orchestrant le pipeline complet du job board :
1. Extraction des offres depuis Adzuna + chargement dans Snowflake (RAW)
2. Transformation des données avec dbt (staging + marts)
3. Tests de qualité des données avec dbt
"""

from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator


DBT_PROJECT_DIR = "/opt/airflow/job_board_dbt"
DBT_PROFILES_DIR = "/opt/airflow/job_board_dbt"


@dag(
    dag_id="job_board_pipeline",
    description="Extraction Adzuna -> Snowflake -> dbt run -> dbt test",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["job-board", "dbt", "snowflake"],
)
def job_board_pipeline():

    extract_and_load = BashOperator(
        task_id="extract_and_load",
        bash_command="python /opt/airflow/extraction/adzuna_extractor.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"dbt run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"dbt test --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    extract_and_load >> dbt_run >> dbt_test


job_board_pipeline()