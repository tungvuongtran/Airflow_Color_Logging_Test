from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import os
import subprocess
import sys
import logging
import traceback
import random

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Function that generates logs at various levels
def generate_test_logs(**context):
    logger = logging.getLogger('airflow.task')
    
    # Regular log messages
    logger.info("This is a standard INFO log message")
    logger.debug("This is a DEBUG level message that might not show depending on log level")
    
    # Some warning logs
    logger.warning("This is a WARNING message that should appear in yellow")
    logger.warning("Another WARNING: This task might be slow")
    
    # Error logs that should be highlighted
    logger.error("This is an ERROR message that should appear in bold red")
    logger.error("Another ERROR: Something went wrong with parameter X")
    
    # Log with the word "error" that should be caught by the handler
    logger.info("This message contains the word 'error' and should be partially highlighted")
    
    # Log with the word "exception" that should be caught by the handler
    logger.info("This message mentions an exception and should also be highlighted")
    
    # Generate a fake stack trace
    try:
        # Deliberately cause an exception
        result = 1 / 0
    except Exception as e:
        logger.error(f"Caught an exception: {e}")
        logger.error(traceback.format_exc())
    
    return "Log test completed"

# Function to run Behave tests with colored logging
def run_behave_with_colored_logs(**context):
    logger = logging.getLogger('airflow.task')
    
    logger.info("Starting Behave test execution with colored logging")
    
    # Get the project root directory
    airflow_home = os.environ.get('AIRFLOW_HOME')
    project_root = os.path.abspath(os.path.dirname(airflow_home))
    
    # Path to Behave tests
    test_path = os.path.join(project_root, 'tests', 'features')
    
    # Log some information
    logger.info(f"AIRFLOW_HOME: {airflow_home}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Test path: {test_path}")
    
    # Add some artificial delays and progress updates
    logger.info("Preparing test environment...")
    
    # Simulate test execution with various log outcomes
    test_scenarios = [
        {"name": "Login Test", "result": "pass"},
        {"name": "Data Validation", "result": "pass"},
        {"name": "API Integration", "result": "fail"},
        {"name": "Database Connection", "result": "error"},
        {"name": "User Profile", "result": "pass"},
    ]
    
    logger.info("Running test scenarios...")
    
    for scenario in test_scenarios:
        scenario_name = scenario["name"]
        result = scenario["result"]
        
        logger.info(f"Executing scenario: {scenario_name}")
        
        if result == "pass":
            logger.info(f"Scenario '{scenario_name}' PASSED")
        elif result == "fail":
            logger.warning(f"Scenario '{scenario_name}' FAILED")
            logger.error(f"Assertion error in '{scenario_name}': Expected 'A' but got 'B'")
        elif result == "error":
            logger.error(f"Exception occurred in scenario '{scenario_name}'")
            logger.error("ConnectionError: Could not connect to database, connection timed out")
            logger.error("Traceback: \n" + 
                      "  File \"features/steps/database_steps.py\", line 45, in connect_to_database\n" +
                      "    conn = establish_connection()\n" +
                      "  File \"features/utils/db.py\", line 23, in establish_connection\n" +
                      "    raise ConnectionError('Could not connect to database')")
    
    # Generate random results summary
    passed = random.randint(10, 20)
    failed = random.randint(0, 5)
    errors = random.randint(0, 3)
    skipped = random.randint(0, 2)
    
    if failed > 0 or errors > 0:
        logger.error(f"Test execution completed with failures: {failed} failed, {errors} errors")
    else:
        logger.info(f"All tests passed successfully!")
    
    logger.info(f"Test Summary: {passed} passed, {failed} failed, {errors} errors, {skipped} skipped")
    
    # Return success for the task even if there were test failures
    # This is so our DAG completes successfully for demonstration purposes
    return "Behave tests executed with colored logging"

# Function that simulates actual Behave test execution
def run_real_behave_tests(**context):
    logger = logging.getLogger('airflow.task')
    
    logger.info("Starting actual Behave test execution")
    
    try:
        # Get paths
        airflow_home = os.environ.get('AIRFLOW_HOME')
        project_root = os.path.abspath(os.path.dirname(airflow_home))
        test_path = os.path.join(project_root, 'tests', 'features')
        
        # Create reports directory
        reports_dir = os.path.join(airflow_home, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for report file names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_report = os.path.join(reports_dir, f'behave_results_{timestamp}.json')
        
        # Run Behave (use --dry-run if you want to avoid actually running tests)
        logger.info(f"Running Behave tests from {test_path}")
        
        cmd = [
            'behave',
            test_path,
            '--format', 'json.pretty',
            '--outfile', json_report,
            # Add '--dry-run' flag here if you want to simulate without actually running tests
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        # Log the output
        if result.stdout:
            logger.info("Behave stdout:")
            for line in result.stdout.splitlines():
                logger.info(line)
        
        # Check for errors in stderr
        if result.stderr:
            logger.error("Behave stderr:")
            for line in result.stderr.splitlines():
                logger.error(line)
        
        # Log the return code
        if result.returncode != 0:
            logger.error(f"Behave tests failed with return code {result.returncode}")
        else:
            logger.info("Behave tests completed successfully")
        
        return "Real Behave tests executed"
        
    except Exception as e:
        logger.error(f"Exception running Behave tests: {e}")
        logger.error(traceback.format_exc())
        raise

# Create the DAG
with DAG(
    'color_log_test',
    default_args=default_args,
    description='Test DAG for color log handler',
    schedule_interval=None,  # Set to None for manual triggering
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['tests', 'logs', 'color'],
) as dag:

    # Task 1: Verify environment setup
    setup_check = BashOperator(
        task_id='setup_check',
        bash_command='''
        echo "AIRFLOW_HOME=$AIRFLOW_HOME"
        echo "Python version: $(python --version)"
        echo "Checking for colorama:"
        pip list | grep colorama
        echo "Checking for behave:"
        pip list | grep behave
        ''',
    )

    # Task 2: Generate test logs with various levels
    test_logs = PythonOperator(
        task_id='generate_test_logs',
        python_callable=generate_test_logs,
        provide_context=True,
    )

    # Task 3: Run simulated Behave tests with colored logging
    run_simulated_tests = PythonOperator(
        task_id='run_behave_with_colored_logs',
        python_callable=run_behave_with_colored_logs,
        provide_context=True,
    )
    
    # Task 4: Attempt to run actual Behave tests if available
    run_actual_tests = PythonOperator(
        task_id='run_real_behave_tests',
        python_callable=run_real_behave_tests,
        provide_context=True,
    )

    # Define task dependencies
    setup_check >> test_logs >> run_simulated_tests >> run_actual_tests