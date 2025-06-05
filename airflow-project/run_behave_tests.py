#!/usr/bin/env python
import os
import subprocess
import sys

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Set environment variables
os.environ['AIRFLOW_HOME'] = os.path.join(project_root, 'airflow_home')

# Path to Behave tests
test_path = os.path.join(project_root, 'tests', 'features')

print(f"Running Behave tests from: {test_path}")
print(f"Using Airflow home: {os.environ['AIRFLOW_HOME']}")

# Run Behave tests
result = subprocess.run(['behave', test_path], capture_output=False)

# Exit with the return code from Behave
sys.exit(result.returncode)