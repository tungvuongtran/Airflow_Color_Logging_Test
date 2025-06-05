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

# Function to run Behave tests with HTML reports
def run_behave_tests_with_reports(**context):
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.environ.get('AIRFLOW_HOME'), '..'))
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(project_root, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Path to Behave tests
    test_path = os.path.join(project_root, 'tests', 'features')
    
    # Configure environment for Behave tests
    test_env = os.environ.copy()
    test_env['AIRFLOW_HOME'] = os.environ.get('AIRFLOW_HOME')
    
    # Generate timestamp for report file names
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_report = os.path.join(reports_dir, f'behave_results_{timestamp}.json')
    html_report = os.path.join(reports_dir, f'behave_results_{timestamp}.html')
    
    # Run Behave tests with multiple formatters
    result = subprocess.run(
        [
            'behave', 
            test_path,
            '--format', 'json.pretty', '--outfile', json_report,
            '--format', 'behave_html_formatter:HTMLFormatter', '--outfile', html_report
        ],
        capture_output=True,
        text=True,
        env=test_env
    )
    
    # Store file paths in XCom
    context['ti'].xcom_push(key='json_report_path', value=json_report)
    context['ti'].xcom_push(key='html_report_path', value=html_report)
    context['ti'].xcom_push(key='behave_returncode', value=result.returncode)
    
    # Print outputs for logging
    print(f"JSON report saved to: {json_report}")
    print(f"HTML report saved to: {html_report}")
    
    # If tests fail, the task should fail
    if result.returncode != 0:
        print(f"Behave tests failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise Exception("Behave tests failed")
        
    return "Behave tests completed successfully with reports generated"

# Create the DAG
with DAG(
    'behave_tests_with_reports',
    default_args=default_args,
    description='Run Behave tests with HTML reporting',
    schedule_interval=None,  # Set to None for manual triggering
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['tests', 'behave', 'reporting'],
) as dag:

    # Task to ensure environment is set up correctly
    setup_env = BashOperator(
        task_id='setup_environment',
        bash_command='echo "AIRFLOW_HOME=$AIRFLOW_HOME"; mkdir -p $AIRFLOW_HOME/../reports',
    )

    # Task to run the Behave tests with reporting
    run_tests = PythonOperator(
        task_id='run_behave_tests',
        python_callable=run_behave_tests_with_reports,
        provide_context=True,
    )

    # Task to display the report location
    report_info = BashOperator(
        task_id='report_info',
        bash_command='echo "HTML report available at: $(ls -la $AIRFLOW_HOME/../reports/behave_results_*.html | tail -1)"',
    )

    # Define task dependencies
    setup_env >> run_tests >> report_info