# Evaluation Report Structure

The evaluation report is returned as an `EvaluationReport` object with the following structure:

```python
EvaluationReport(
    name='1st-test-with-judge',           # Name of the evaluation
    cases=[ReportCase, ...],               # List of test cases
    failures=[],                           # List of failures
    trace_id='019a3967e787e09eed0fbc15748744c7',  # Trace ID for debugging
    span_id='54c4d03561091fa7'             # Span ID for debugging
)
```

## ReportCase Structure

Each case in `report.cases` contains:

```python
ReportCase(
    name='uppercase_basic',                # Test case name
    inputs='hello world',                  # Input data
    metadata=None,                         # Optional metadata
    expected_output='HELLO WORLD',         # Expected result
    output='HELLO WORLD',                  # Actual output
    metrics={},                            # Performance metrics
    attributes={},                         # Additional attributes
    scores={},                             # Numerical scores
    labels={},                             # Labels/tags
    assertions={                           # Evaluation results (key structure!)
        'Equals-expected': EvaluationResult(...),
        'Contains-Hello': EvaluationResult(...),
        'LLMJudge': EvaluationResult(...)
    },
    task_duration=0.001316,                # Task execution time
    total_duration=1.704737,               # Total duration including evals
    trace_id='...',                        # Trace ID
    span_id='...',                         # Span ID
    evaluator_failures=[]                  # List of evaluator failures
)
```

## EvaluationResult Structure

Each assertion contains an `EvaluationResult` object:

```python
EvaluationResult(
    name='Equals-expected',                # Assertion name
    value=True,                            # Pass/Fail (Boolean)
    reason=None,                           # Optional explanation
    source=EvaluatorSpec(                  # Evaluator metadata
        name='EqualsExpected',
        arguments=('Equals-expected',)
    )
)
```

# Accessing Report Data

## Basic Access Patterns

**1. Get all cases:**
```python
all_cases = report.cases
```

**2. Access specific assertion for a case:**
```python
equals_result = report.cases[0].assertions['Equals-expected']
print(equals_result.value)  # True or False
print(equals_result.reason)  # Explanation (if available)
```

**3. Get case input/output:**
```python
case = report.cases[0]
print(f"Input: {case.inputs}")
print(f"Expected: {case.expected_output}")
print(f"Actual: {case.output}")
```

# Analysis Patterns

## Pattern 1: Extract Specific Assertion Values

**Get list of True/False for a specific assertion:**
```python
equals_values = [
    case.assertions['Equals-expected'].value
    for case in report.cases
]
# Result: [True, True, False, True]
```

**Convert to 1/0 for numerical analysis:**
```python
equals_binary = [
    int(case.assertions['Equals-expected'].value)
    for case in report.cases
]
# Result: [1, 1, 0, 1]
```

## Pattern 2: Create Case-to-Result Dictionaries

**Map case names to assertion results:**
```python
equals_dict = {
    case.name: case.assertions['Equals-expected'].value
    for case in report.cases
}
# Result: {'uppercase_basic': True, 'uppercase_with_numbers': True}
```

**Get all assertions for each case:**
```python
all_assertions_by_case = {
    case.name: {
        assertion_name: result.value
        for assertion_name, result in case.assertions.items()
    }
    for case in report.cases
}
# Result: {
#   'uppercase_basic': {
#     'Equals-expected': True,
#     'Contains-Hello': True,
#     'LLMJudge': True
#   },
#   ...
# }
```

## Pattern 3: Aggregate Statistics

**Count passes/failures for specific assertion:**
```python
equals_values = [case.assertions['Equals-expected'].value for case in report.cases]
stats = {
    'passed': sum(equals_values),
    'failed': len(equals_values) - sum(equals_values),
    'total': len(equals_values),
    'pass_rate': sum(equals_values) / len(equals_values) * 100
}
# Result: {'passed': 3, 'failed': 1, 'total': 4, 'pass_rate': 75.0}
```

**Summary across all assertions:**
```python
from collections import Counter

# Get pass rates for all assertions
assertion_stats = {}
for assertion_name in report.cases[0].assertions.keys():
    values = [case.assertions[assertion_name].value for case in report.cases]
    assertion_stats[assertion_name] = {
        'passed': sum(values),
        'total': len(values),
        'pass_rate': sum(values) / len(values) * 100
    }

# Result: {
#   'Equals-expected': {'passed': 3, 'total': 4, 'pass_rate': 75.0},
#   'Contains-Hello': {'passed': 4, 'total': 4, 'pass_rate': 100.0},
#   'LLMJudge': {'passed': 2, 'total': 4, 'pass_rate': 50.0}
# }
```

## Pattern 4: Filter and Analyze Failed Cases

**Get all failed cases for a specific assertion:**
```python
failed_cases = [
    case for case in report.cases
    if not case.assertions['Equals-expected'].value
]

# Detailed failure analysis
for case in failed_cases:
    print(f"Case: {case.name}")
    print(f"  Input: {case.inputs}")
    print(f"  Expected: {case.expected_output}")
    print(f"  Actual: {case.output}")
    print(f"  Reason: {case.assertions['Equals-expected'].reason}")
```

**Find cases that failed any assertion:**
```python
any_failure_cases = [
    case for case in report.cases
    if not all(result.value for result in case.assertions.values())
]
```

## Pattern 5: Performance Analysis

**Analyze execution times:**
```python
timing_data = [
    {
        'case': case.name,
        'task_duration': case.task_duration,
        'total_duration': case.total_duration,
        'eval_overhead': case.total_duration - case.task_duration
    }
    for case in report.cases
]

# Calculate average times
avg_task_time = sum(d['task_duration'] for d in timing_data) / len(timing_data)
avg_total_time = sum(d['total_duration'] for d in timing_data) / len(timing_data)
```

## Pattern 6: Export for Analysis

**Convert to pandas DataFrame for analysis:**
```python
import pandas as pd

# Flatten report to DataFrame
rows = []
for case in report.cases:
    row = {
        'case_name': case.name,
        'input': case.inputs,
        'expected': case.expected_output,
        'output': case.output,
        'task_duration': case.task_duration,
        'total_duration': case.total_duration
    }
    # Add all assertion values
    for assertion_name, result in case.assertions.items():
        row[f'assertion_{assertion_name}'] = result.value
    rows.append(row)

df = pd.DataFrame(rows)
```

**Export to JSON for external tools:**
```python
import json

report_data = {
    'name': report.name,
    'summary': {
        'total_cases': len(report.cases),
        'passed': sum(all(r.value for r in case.assertions.values()) for case in report.cases)
    },
    'cases': [
        {
            'name': case.name,
            'inputs': case.inputs,
            'output': case.output,
            'assertions': {
                name: {'value': result.value, 'reason': result.reason}
                for name, result in case.assertions.items()
            }
        }
        for case in report.cases
    ]
}

with open('eval_results.json', 'w') as f:
    json.dump(report_data, f, indent=2)
```

# Key Takeaways

1. **Hierarchical Structure**: Report → Cases → Assertions → EvaluationResult
2. **Assertions are Dictionaries**: Access via `case.assertions['assertion-name']`
3. **Value is Boolean**: `result.value` returns True/False for pass/fail
4. **Flexible Analysis**: Can aggregate, filter, export in various formats
5. **Performance Tracking**: `task_duration` vs `total_duration` shows eval overhead
