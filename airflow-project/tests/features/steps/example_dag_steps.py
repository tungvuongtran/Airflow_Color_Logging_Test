from behave import given, then
import sys
import os
from airflow.models import DagBag

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
airflow_home = os.path.join(project_root, 'airflow_home')
dags_folder = os.path.join(airflow_home, 'dags')

@given('the DAG "{dag_id}" is defined')
def dag_is_defined(context, dag_id):
    dagbag = DagBag(dag_folder=dags_folder)
    context.dag_errors = dagbag.import_errors
    context.dag = dagbag.get_dag(dag_id)
    assert context.dag is not None, f"DAG {dag_id} not found"

@then('it should have the correct structure')
def check_dag_structure(context):
    dag = context.dag
    assert len(dag.tasks) == 2, f"Expected 2 tasks, got {len(dag.tasks)}"
    assert "hello_task" in [task.task_id for task in dag.tasks], "hello_task not found"
    assert "goodbye_task" in [task.task_id for task in dag.tasks], "goodbye_task not found"
    
    # Check task dependencies
    for task in dag.tasks:
        if task.task_id == "hello_task":
            downstream_task_ids = [t.task_id for t in task.downstream_list]
            assert "goodbye_task" in downstream_task_ids, "hello_task should be upstream of goodbye_task"

@given('the "{task_id}" in DAG "{dag_id}" is executed')
def execute_task(context, task_id, dag_id):
    dagbag = DagBag(dag_folder=dags_folder)
    dag = dagbag.get_dag(dag_id)
    task = dag.get_task(task_id)
    context.task_instance = task.execute(context={})
    
@then('the task should return "{expected_output}"')
def check_task_output(context, expected_output):
    assert context.task_instance == expected_output, f"Expected {expected_output}, got {context.task_instance}"