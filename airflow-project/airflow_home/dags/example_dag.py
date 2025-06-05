from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def say_hello(**kwargs):
    print("Hello from Airflow!")
    return "Hello"

def say_goodbye(**kwargs):
    print("Goodbye from Airflow!")
    return "Goodbye"

with DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=say_hello,
    )

    goodbye_task = PythonOperator(
        task_id='goodbye_task',
        python_callable=say_goodbye,
    )

    hello_task >> goodbye_task