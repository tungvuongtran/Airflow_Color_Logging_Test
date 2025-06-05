import os
import sys

def before_all(context):
    # Get the absolute path to the project root - adjust this path based on where tests run from
    # When running from a DAG, the current directory might be the Airflow home
    airflow_home = os.environ.get('AIRFLOW_HOME')
    project_root = os.path.abspath(os.path.join(airflow_home, '..'))
    
    # Set up environment variables
    os.environ['AIRFLOW_HOME'] = airflow_home
    
    # Add the project root to the Python path to allow imports
    sys.path.append(project_root)
    # Add the dags directory to the Python path
    sys.path.append(os.path.join(airflow_home, 'dags'))
    
    print(f"Behave test environment set up with AIRFLOW_HOME: {airflow_home}")
    print(f"Project root: {project_root}")
    print(f"Python path: {sys.path}")