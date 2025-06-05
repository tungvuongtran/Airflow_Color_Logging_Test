Feature: Test Example DAG
  We want to test our example DAG

  Scenario: DAG loads correctly
    Given the DAG "example_dag" is defined
    Then it should have the correct structure

  Scenario: DAG tasks execute correctly
    Given the "hello_task" in DAG "example_dag" is executed
    Then the task should return "Hello"
    
    Given the "goodbye_task" in DAG "example_dag" is executed
    Then the task should return "Goodbye"