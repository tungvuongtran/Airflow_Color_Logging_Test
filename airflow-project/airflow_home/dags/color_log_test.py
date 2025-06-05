from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging

def log_levels():
    logging.debug("Debug message")
    logging.info("Info message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message with exception")

with DAG(
    dag_id='test_color_logging',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
) as dag:
    PythonOperator(
        task_id='log_task',
        python_callable=log_levels,
    )
