import logfire
from dotenv import load_dotenv
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Contains, EqualsExpected, LLMJudge

# from rich import print
# from rich.console import Console

load_dotenv()
logfire.configure()
# console = Console()

# Create a dataset with test cases
dataset = Dataset(
    cases=[
        Case(
            name="uppercase_basic",
            inputs="hello world",
            expected_output="HELLO WORLD",
        ),
        Case(
            name="uppercase_with_numbers",
            inputs="hello 123",
            expected_output="HELLO 123",
        ),
    ],
    evaluators=[
        EqualsExpected(
            evaluation_name="Equals-expected"
        ),  # Check exact match with expected_output
        Contains(
            value="HELLO", case_sensitive=True, evaluation_name="Contains-Hello"
        ),  # Check contains "HELLO"
        LLMJudge(
            rubric="Response is accurate and helpful",
            include_input=True,
        ),
    ],
)


# Define the function to evaluate
def uppercase_text(text: str) -> str:
    return text.upper()


# Run the evaluation
report = dataset.evaluate_sync(uppercase_text, name="1st-test-with-judge-console-1")
# Note that currently I cannot add metadata to the experiement though it is mentioned in this doc https://ai.pydantic.dev/evals/how-to/metrics-attributes/#experiment-level-metadata or it seems like experiment metadata is only available in .evaluate rather than .evaluate_sync

# Print the results
report.print()
# print(report)
# console.print(report.console_table()) # this one is very similar to report.print()
"""
        Evaluation Summary: uppercase_text
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Case ID                ┃ Assertions ┃ Duration ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ uppercase_basic        │ ✔✔         │     10ms │
├────────────────────────┼────────────┼──────────┤
│ uppercase_with_numbers │ ✔✔         │     10ms │
├────────────────────────┼────────────┼──────────┤
│ Averages               │ 100.0% ✔   │     10ms │
└────────────────────────┴────────────┴──────────┘
"""
