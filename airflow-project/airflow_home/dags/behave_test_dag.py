from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import os
import subprocess
import sys

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to run Behave tests and return results
def run_behave_tests(**context):
    # Get the project root directory - adjust this path based on your project structure
    project_root = os.path.abspath(os.path.join(os.environ.get('AIRFLOW_HOME'), '..'))
    
    # Path to Behave tests
    test_path = os.path.join(project_root, 'tests', 'features')
    
    # Configure environment for Behave tests
    test_env = os.environ.copy()
    test_env['AIRFLOW_HOME'] = os.environ.get('AIRFLOW_HOME')
    
    print(f"Running Behave tests from: {test_path}")
    print(f"Using Airflow home: {test_env['AIRFLOW_HOME']}")
    
    # Run Behave tests and capture output
    result = subprocess.run(
        ['behave', test_path, '--format', 'json.pretty', '--outfile', 'behave_results.json'],
        capture_output=True,
        text=True,
        env=test_env
    )
    
    # Store test output in XCom for later tasks to use
    context['ti'].xcom_push(key='behave_stdout', value=result.stdout)
    context['ti'].xcom_push(key='behave_stderr', value=result.stderr)
    context['ti'].xcom_push(key='behave_returncode', value=result.returncode)
    
    # If tests fail, the task should fail
    if result.returncode != 0:
        print(f"Behave tests failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise Exception("Behave tests failed")
        
    return "Behave tests completed successfully"

# Function to process and analyze Behave test results
def analyze_test_results(**context):
    import json
    
    # Get test results from previous task
    stdout = context['ti'].xcom_pull(task_ids='run_behave_tests', key='behave_stdout')
    stderr = context['ti'].xcom_pull(task_ids='run_behave_tests', key='behave_stderr')
    returncode = context['ti'].xcom_pull(task_ids='run_behave_tests', key='behave_returncode')
    
    print(f"Test execution return code: {returncode}")
    
    # Try to parse JSON results file
    try:
        with open('behave_results.json', 'r') as f:
            results = json.load(f)
            
        # Count passing and failing scenarios
        total_scenarios = 0
        passed_scenarios = 0
        failed_scenarios = 0
        
        for feature in results:
            for scenario in feature.get('elements', []):
                if scenario.get('type') == 'scenario':
                    total_scenarios += 1
                    # Check if any step failed
                    has_failed_step = any(step.get('result', {}).get('status') == 'failed' 
                                         for step in scenario.get('steps', []))
                    if has_failed_step:
                        failed_scenarios += 1
                    else:
                        passed_scenarios += 1
        
        print(f"Test Summary: {passed_scenarios}/{total_scenarios} scenarios passed")
        print(f"Failed scenarios: {failed_scenarios}")
        
        if failed_scenarios > 0:
            return "Some tests failed"
        else:
            return "All tests passed"
        
    except Exception as e:
        print(f"Error analyzing test results: {e}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return "Error analyzing test results"

# Create the DAG
with DAG(
    'behave_tests',
    default_args=default_args,
    description='Run Behave tests for Airflow DAGs',
    schedule_interval=None,  # Set to None for manual triggering
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['tests', 'behave'],
) as dag:

    # Task to ensure environment is set up correctly
    setup_env = BashOperator(
        task_id='setup_environment',
        bash_command='echo "AIRFLOW_HOME=$AIRFLOW_HOME"; echo "Current directory: $(pwd)"; ls -la $AIRFLOW_HOME',
    )

    # Task to run the Behave tests
    run_tests = PythonOperator(
        task_id='run_behave_tests',
        python_callable=run_behave_tests,
        provide_context=True,
    )

    # Task to analyze and report test results
    analyze_results = PythonOperator(
        task_id='analyze_test_results',
        python_callable=analyze_test_results,
        provide_context=True,
    )

    # Define task dependencies
    setup_env >> run_tests >> analyze_results