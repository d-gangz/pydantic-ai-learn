<!--
Document Type: Guide
Purpose: Comprehensive guide for junior developers to implement and use Pydantic AI evaluations
Context: Created as a practical reference for implementing evals in Pydantic AI projects
Key Topics: Cases, datasets, evaluators (built-in, custom, LLM judge, span-based), dataset management, evaluation workflows
Target Use: Step-by-step implementation guide and reference for running AI system evaluations
-->

# Pydantic AI Evals Guide for Junior Developers

A practical guide to implementing evaluations (evals) for AI systems using Pydantic AI.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Creating Cases & Datasets](#creating-cases--datasets)
3. [Understanding Evaluators](#understanding-evaluators)
4. [Built-in Evaluators](#built-in-evaluators)
5. [Custom Evaluators](#custom-evaluators)
6. [LLM Judge Evaluators](#llm-judge-evaluators)
7. [Span-Based Evaluators](#span-based-evaluators)
8. [Dataset Management](#dataset-management)
9. [Complete Example](#complete-example)

---

## Core Concepts

Pydantic Evals is a testing framework designed specifically for AI systems. Unlike traditional unit tests, it handles probabilistic outputs and allows you to define test cases and evaluation criteria.

**Four Main Components:**

1. **Case**: A single test scenario with inputs and optional expected outputs
2. **Dataset**: A collection of test cases and evaluators
3. **Evaluator**: Logic that assesses task outputs (pass/fail, scores, or labels)
4. **Experiment**: Running your task function against all dataset cases

**Basic Workflow:**
```
Define Dataset → Execute via dataset.evaluate(task_function) → Analyze EvaluationReport
```

📚 [Learn more about core concepts](https://ai.pydantic.dev/evals/core-concepts/)

---

## Creating Cases & Datasets

### Creating a Case

A `Case` represents a single test scenario:

```python
from pydantic_evals import Case

# Basic case
case = Case(
    name='simple_addition',
    inputs={'a': 1, 'b': 2},
    expected_output=3
)

# Case with metadata (recommended!)
case_with_metadata = Case(
    name='complex_math',
    inputs={'expression': '2 + 2 * 3'},
    expected_output=8,
    metadata={
        'difficulty': 'medium',
        'category': 'order_of_operations',
        'description': 'Tests operator precedence'
    }
)
```

**Key Parameters:**
- `name` (optional): Identifies the case in reports
- `inputs` (required): Data passed to your task
- `expected_output` (optional): Reference output for comparison
- `metadata` (optional): Additional contextual information for evaluators
- `evaluators` (optional): Case-specific evaluators

💡 **Best Practice**: Always include metadata to organize tests and provide context to evaluators.

### Creating a Dataset

```python
from pydantic_evals import Dataset
from pydantic_evals.evaluators import EqualsExpected

# Create dataset with cases
dataset = Dataset(
    name='math_operations',
    cases=[
        Case(name='add', inputs={'a': 1, 'b': 2}, expected_output=3),
        Case(name='multiply', inputs={'a': 3, 'b': 4}, expected_output=12),
    ],
    evaluators=[EqualsExpected()]
)

# Build dataset incrementally
dataset = Dataset(name='my_tests', cases=[], evaluators=[])
dataset.add_case(Case(name='test1', inputs={'x': 1}, expected_output=2))
dataset.add_evaluator(EqualsExpected())
```

📚 [Dataset API documentation](https://ai.pydantic.dev/api/pydantic_evals/dataset/#pydantic_evals.dataset)

---

## Understanding Evaluators

Evaluators analyze task outputs and provide structured feedback. They receive an `EvaluatorContext` containing:
- Task inputs and outputs
- Expected outputs (if provided)
- Execution duration
- Metadata and custom attributes

**Three Main Types:**

1. **Deterministic Checks**: Fast, rule-based (microseconds, zero cost)
2. **LLM-as-a-Judge**: Uses AI for subjective assessment (slower, costly)
3. **Custom Evaluators**: Domain-specific logic

**Return Types:**
- **Boolean**: Pass/fail assertions
- **Number**: Quantitative scores (typically 0.0-1.0)
- **String**: Categorical labels
- **Dictionary**: Multiple results simultaneously

📚 [Evaluators overview](https://ai.pydantic.dev/evals/evaluators/overview/)
📚 [Evaluator API reference](https://ai.pydantic.dev/api/pydantic_evals/evaluators/#pydantic_evals.evaluators.Evaluator)

---

## Built-in Evaluators

Pydantic provides seven built-in evaluators for common scenarios:

### 1. EqualsExpected
Verifies output exactly matches expected output from the case.

```python
from pydantic_evals.evaluators import EqualsExpected

dataset = Dataset(
    cases=[Case(inputs={'x': 5}, expected_output=10)],
    evaluators=[EqualsExpected()]
)
```

### 2. Equals
Compares output against a specific value.

```python
from pydantic_evals.evaluators import Equals

# Check for specific value
evaluator = Equals(value="success")
```

### 3. Contains
Searches for a value or substring within output.

```python
from pydantic_evals.evaluators import Contains

# Case-sensitive substring check
evaluator = Contains(value="error", case_sensitive=True)

# Case-insensitive
evaluator = Contains(value="SUCCESS", case_sensitive=False)
```

### 4. IsInstance
Validates output type.

```python
from pydantic_evals.evaluators import IsInstance

# Check if output is a string
evaluator = IsInstance(type_name="str")

# Check for custom class
evaluator = IsInstance(type_name="MyCustomClass")
```

### 5. MaxDuration
Ensures task completes within time threshold.

```python
from pydantic_evals.evaluators import MaxDuration
from datetime import timedelta

# Max 2 seconds
evaluator = MaxDuration(duration=2.0)

# Or use timedelta
evaluator = MaxDuration(duration=timedelta(seconds=2))
```

### 6. LLMJudge
Uses an LLM to evaluate subjective qualities (covered in detail below).

### 7. HasMatchingSpan
Checks OpenTelemetry spans for agent evaluation (covered in span-based section).

💡 **Best Practice**: Combine fast deterministic checks first (IsInstance, Contains, MaxDuration) before running expensive LLM evaluations to fail fast.

📚 [Built-in evaluators documentation](https://ai.pydantic.dev/evals/evaluators/built-in/)

---

## Custom Evaluators

Create custom evaluators for domain-specific logic, external API validation, or specialized metrics.

### Implementation Pattern

```python
from dataclasses import dataclass
from pydantic_evals import Evaluator, EvaluatorContext

@dataclass
class MyCustomEvaluator(Evaluator):
    """Custom evaluator with configurable parameters."""
    threshold: float = 0.8  # Configuration parameter

    def evaluate(self, ctx: EvaluatorContext) -> bool | float | str | dict:
        """
        Implement evaluation logic.

        ctx provides:
        - ctx.inputs: Task inputs
        - ctx.output: Task output
        - ctx.expected_output: Expected output (if provided)
        - ctx.metadata: Case metadata
        - ctx.duration: Execution time
        """
        # Your evaluation logic here
        score = len(ctx.output) / 100

        # Can return different types:
        # return True  # Boolean
        # return 0.85  # Numeric score
        # return "valid"  # String label
        # return {"score": 0.85, "quality": "high"}  # Multiple metrics

        return score > self.threshold
```

### Example: SQL Query Validator

```python
from dataclasses import dataclass
from pydantic_evals import Evaluator, EvaluatorContext, EvaluationReason
import sqlparse

@dataclass
class ValidSQL(Evaluator):
    """Validates if output is syntactically correct SQL."""

    def evaluate(self, ctx: EvaluatorContext) -> EvaluationReason:
        try:
            parsed = sqlparse.parse(ctx.output)
            if len(parsed) == 0:
                return EvaluationReason(
                    value=False,
                    reason="Empty or invalid SQL"
                )

            return EvaluationReason(
                value=True,
                reason=f"Valid SQL with {len(parsed)} statement(s)"
            )
        except Exception as e:
            return EvaluationReason(
                value=False,
                reason=f"SQL parsing error: {str(e)}"
            )
```

### Async Evaluators

For I/O-bound operations (API calls, database queries):

```python
@dataclass
class ExternalAPIValidator(Evaluator):
    api_url: str

    async def evaluate(self, ctx: EvaluatorContext) -> bool:
        """Async evaluation for external API calls."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={"data": ctx.output}
            )
            return response.json()["is_valid"]
```

### Multiple Metrics from One Evaluator

```python
@dataclass
class ComprehensiveTextAnalysis(Evaluator):
    """Returns multiple metrics from a single evaluation."""

    def evaluate(self, ctx: EvaluatorContext) -> dict:
        text = ctx.output

        return {
            "word_count": len(text.split()),
            "has_greeting": "hello" in text.lower(),
            "politeness_score": self._calculate_politeness(text),
            "readability": "easy" if len(text) < 100 else "complex"
        }
```

💡 **Best Practices:**
- Keep evaluators focused on single checks
- Handle missing data gracefully
- Provide meaningful explanatory text with `EvaluationReason`
- Implement timeouts for external service calls

📚 [Custom evaluators documentation](https://ai.pydantic.dev/evals/evaluators/custom/)

---

## LLM Judge Evaluators

Use LLMs to assess subjective qualities like factual accuracy, helpfulness, tone, and completeness.

### When to Use LLM Judges

**✅ Good Use Cases:**
- Factual accuracy
- Helpfulness and relevance
- Tone and style compliance
- Completeness of responses
- Following complex instructions
- RAG groundedness
- Citation accuracy

**❌ Poor Use Cases:**
- Format validation → Use `IsInstance` or regex
- Exact matching → Use `EqualsExpected`
- Performance checks → Use `MaxDuration`
- Deterministic logic → Use custom evaluators

### Basic Usage

```python
from pydantic_evals.evaluators import LLMJudge

# Simple assertion (pass/fail)
judge = LLMJudge(
    rubric="Response is factually accurate and contains no hallucinations"
)

# Numeric score
judge = LLMJudge(
    rubric="Rate the helpfulness of the response on a scale of 0.0 to 1.0",
    output_type="score"
)
```

### Advanced Configuration

```python
from pydantic_evals.evaluators import LLMJudge

judge = LLMJudge(
    rubric="""
    Evaluate the response based on:
    1. Directly answers the user's question
    2. Provides accurate information without hallucination
    3. Uses professional tone
    4. Is concise but complete
    """,
    model="gpt-4o",  # or "gpt-4o-mini", "claude-3-opus-20240229"
    temperature=0.0,  # For consistency
    include_input=True,  # Judge sees the input
    include_expected_output=True,  # Judge sees expected output
    output_type="assertion"  # or "score" or "both"
)
```

### Context Control

Control what information the judge sees:

```python
# Output only (default)
judge = LLMJudge(rubric="...")

# Output + Input
judge = LLMJudge(
    rubric="...",
    include_input=True
)

# Output + Input + Expected Output
judge = LLMJudge(
    rubric="...",
    include_input=True,
    include_expected_output=True
)
```

### Best Practices for LLM Judges

1. **Be Specific in Rubrics**:
   - ❌ Bad: "good response"
   - ✅ Good: "Response directly answers the user question without hallucination"

2. **Use Temperature 0.0**: For consistency in evaluation

3. **Choose the Right Model**:
   - `gpt-4o-mini`: Simple checks, cost-sensitive
   - `gpt-4o`: General purpose (default)
   - `claude-3-opus`: Nuanced evaluation, highest quality

4. **Combine with Deterministic Checks**: Run fast checks first to fail early

5. **Understand Limitations**:
   - Non-deterministic: Same output may score differently
   - Costly: Each evaluation triggers API calls
   - Model biases: Judges inherit training data biases

### Mitigation Strategies

```python
# Use multiple judges for important evaluations
dataset = Dataset(
    cases=[...],
    evaluators=[
        LLMJudge(rubric="...", model="gpt-4o"),
        LLMJudge(rubric="...", model="claude-3-opus-20240229"),
        # Also add deterministic checks
        MaxDuration(duration=5.0),
        Contains(value="citation")
    ]
)
```

📚 [LLM Judge documentation](https://ai.pydantic.dev/evals/evaluators/llm-judge/)

---

## Span-Based Evaluators

Evaluate **how** your AI system executes, not just **what** it produces. Particularly valuable for complex multi-step agents.

### What Are Spans?

Spans are OpenTelemetry traces that capture execution details like function calls, tool usage, and agent interactions.

### Setup Requirements

```python
import logfire

# Configure Logfire to capture spans
logfire.configure()
```

### Basic Usage with HasMatchingSpan

```python
from pydantic_evals.evaluators import HasMatchingSpan

# Check if a specific tool was called
evaluator = HasMatchingSpan(
    query={"name": "search_database"}
)

# Check for spans with specific attributes
evaluator = HasMatchingSpan(
    query={
        "name": "llm_call",
        "attributes": {"model": "gpt-4"}
    }
)
```

### Common Use Cases

#### 1. RAG Systems: Verify Retrieval Occurred

```python
# Ensure retrieval happened before generation
retrieval_check = HasMatchingSpan(
    query={"name": "retrieve_documents"}
)

rerank_check = HasMatchingSpan(
    query={"name": "rerank_results"}
)
```

#### 2. Multi-Agent Coordination

```python
# Ensure specialist agent was called
specialist_check = HasMatchingSpan(
    query={
        "name": "delegate_to_agent",
        "attributes": {"agent_type": "sql_specialist"}
    }
)
```

#### 3. Tool Verification

```python
# Verify calculator tool was used
tool_check = HasMatchingSpan(
    query={"name": "calculator_tool"}
)
```

#### 4. Performance Assertions

```python
# Check operation completed within time limit
fast_retrieval = HasMatchingSpan(
    query={
        "name": "vector_search",
        "max_duration": 0.5  # 500ms
    }
)
```

### Custom Span-Based Evaluators

For complex span analysis:

```python
from dataclasses import dataclass
from pydantic_evals import Evaluator, EvaluatorContext

@dataclass
class ValidRAGSequence(Evaluator):
    """Ensures RAG steps occur in correct order."""

    def evaluate(self, ctx: EvaluatorContext) -> bool:
        span_tree = ctx.span_tree

        # Check sequence: retrieve → rerank → generate
        retrieve_spans = span_tree.find(name="retrieve_documents")
        rerank_spans = span_tree.find(name="rerank_results")
        generate_spans = span_tree.find(name="generate_response")

        if not (retrieve_spans and rerank_spans and generate_spans):
            return False

        # Verify time ordering
        retrieve_time = retrieve_spans[0].start_time
        rerank_time = rerank_spans[0].start_time
        generate_time = generate_spans[0].start_time

        return retrieve_time < rerank_time < generate_time
```

### Span Query Methods

The `SpanTree` API provides:
- `find()`: Get all matching spans
- `any()`: Check if any span matches
- `all()`: Check if all spans match condition
- `count()`: Count matching spans

```python
@dataclass
class ToolUsageCounter(Evaluator):
    """Counts how many times tools were called."""

    def evaluate(self, ctx: EvaluatorContext) -> dict:
        span_tree = ctx.span_tree

        return {
            "calculator_calls": span_tree.count(name="calculator"),
            "search_calls": span_tree.count(name="search"),
            "total_tool_calls": span_tree.count(
                name_pattern=".*_tool"  # Regex pattern
            )
        }
```

💡 **Best Practice**: Use span-based evaluators for agent systems to ensure correct behavior patterns, not just correct outputs.

📚 [Span-based evaluators documentation](https://ai.pydantic.dev/evals/evaluators/span-based/)

---

## Dataset Management

Organize, save, load, and maintain datasets for reproducible evaluations.

### Saving Datasets

```python
from pydantic_evals import Dataset, Case

dataset = Dataset(
    name='my_tests',
    cases=[...],
    evaluators=[...]
)

# Save as YAML (recommended for readability)
dataset.to_file('my_dataset.yaml')

# Save as JSON
dataset.to_file('my_dataset.json')

# Custom schema path
dataset.to_file(
    'my_dataset.yaml',
    schema_path='./schemas/dataset_schema.json'
)
```

### Loading Datasets

```python
from pydantic_evals import Dataset

# Load from file (auto-detects format)
dataset = Dataset.from_file('my_dataset.yaml')

# Load with custom evaluators
from pydantic_evals.evaluators import EqualsExpected

dataset = Dataset.from_file(
    'my_dataset.yaml',
    evaluators=[EqualsExpected()]
)
```

### Type-Safe Datasets

```python
from pydantic_evals import Dataset
from pydantic import BaseModel

class MathInput(BaseModel):
    a: int
    b: int

class MathMetadata(BaseModel):
    difficulty: str
    category: str

# Type-safe dataset
dataset: Dataset[MathInput, int, MathMetadata] = Dataset(
    cases=[
        Case(
            inputs=MathInput(a=1, b=2),
            expected_output=3,
            metadata=MathMetadata(
                difficulty='easy',
                category='addition'
            )
        )
    ]
)
```

### Dataset Organization Best Practices

1. **Clear Naming**: Use descriptive names
   ```python
   # ❌ Bad
   Case(name='test1', ...)

   # ✅ Good
   Case(name='uppercase_unicode_emoji', ...)
   ```

2. **Organize by Difficulty**: Use metadata
   ```python
   Case(
       name='complex_nested_json',
       inputs={...},
       metadata={'difficulty': 'hard', 'category': 'parsing'}
   )
   ```

3. **Incremental Growth**: Start small, expand as you find edge cases
   ```python
   # Start with core cases
   core_dataset = Dataset(name='core', cases=[...])

   # Add edge cases as discovered
   core_dataset.add_case(
       Case(name='edge_case_unicode', ...)
   )
   ```

4. **Separate by Purpose**: Different datasets for different testing phases
   ```python
   smoke_tests = Dataset(name='smoke', cases=[...])  # Quick validation
   comprehensive_tests = Dataset(name='full', cases=[...])  # Complete suite
   regression_tests = Dataset(name='regression', cases=[...])  # Known bugs
   ```

5. **Version Control**: Commit YAML/JSON datasets to git
   ```bash
   git add datasets/
   git commit -m "Add new edge cases for email parsing"
   ```

### Generating Datasets with LLMs

```python
from pydantic_evals import generate_dataset

# Generate test cases using an LLM
generate_dataset(
    task_description="Parse email addresses from text",
    output_path="email_parsing_dataset.yaml",
    num_cases=20
)
```

📚 [Dataset management documentation](https://ai.pydantic.dev/evals/how-to/dataset-management/)

---

## Complete Example

Here's a full example bringing everything together:

```python
"""
AI system evaluation script using Pydantic Evals.

Input data sources: test_cases/email_extraction.yaml
Output destinations: results/evaluation_report.json
Dependencies: pydantic-ai, logfire (for span tracking)
Key exports: evaluate_email_extraction()
Side effects: Writes evaluation report to disk
"""

from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_evals import Dataset, Case, Evaluator, EvaluatorContext
from pydantic_evals.evaluators import (
    EqualsExpected,
    Contains,
    MaxDuration,
    LLMJudge,
    HasMatchingSpan
)
import logfire
import json

# Configure tracing
logfire.configure()

# Define input/output models
class EmailInput(BaseModel):
    text: str

class EmailOutput(BaseModel):
    emails: list[str]

# Create the AI agent to test
agent = Agent(
    'openai:gpt-4o',
    result_type=EmailOutput,
    system_prompt="Extract all email addresses from the provided text."
)

# Custom evaluator
@dataclass
class ValidEmailFormat(Evaluator):
    """Validates that extracted emails have valid format."""

    def evaluate(self, ctx: EvaluatorContext) -> dict:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        emails = ctx.output.emails
        valid_count = sum(1 for email in emails if re.match(email_pattern, email))

        return {
            "all_valid_format": valid_count == len(emails),
            "valid_count": valid_count,
            "total_count": len(emails)
        }

# Create dataset
dataset = Dataset(
    name='email_extraction_tests',
    cases=[
        Case(
            name='simple_email',
            inputs=EmailInput(text="Contact me at john@example.com"),
            expected_output=EmailOutput(emails=["john@example.com"]),
            metadata={
                'difficulty': 'easy',
                'category': 'single_email'
            }
        ),
        Case(
            name='multiple_emails',
            inputs=EmailInput(
                text="Reach out to alice@company.com or bob@company.com"
            ),
            expected_output=EmailOutput(
                emails=["alice@company.com", "bob@company.com"]
            ),
            metadata={
                'difficulty': 'medium',
                'category': 'multiple_emails'
            }
        ),
        Case(
            name='no_emails',
            inputs=EmailInput(text="No email addresses here!"),
            expected_output=EmailOutput(emails=[]),
            metadata={
                'difficulty': 'easy',
                'category': 'edge_case'
            }
        ),
        Case(
            name='complex_format',
            inputs=EmailInput(
                text="Email: john.doe+tag@sub.example.co.uk"
            ),
            expected_output=EmailOutput(
                emails=["john.doe+tag@sub.example.co.uk"]
            ),
            metadata={
                'difficulty': 'hard',
                'category': 'complex_format'
            }
        )
    ],
    evaluators=[
        # Fast deterministic checks
        MaxDuration(duration=2.0),
        ValidEmailFormat(),

        # LLM judge for quality
        LLMJudge(
            rubric="""
            Evaluate if the extracted emails are:
            1. Complete (no missing emails)
            2. Accurate (no false positives)
            3. Properly formatted
            """,
            include_input=True,
            include_expected_output=True,
            output_type="score"
        ),

        # Span-based evaluation
        HasMatchingSpan(
            query={"name": "llm_call"}  # Verify LLM was invoked
        )
    ]
)

# Save dataset for reuse
dataset.to_file('test_cases/email_extraction.yaml')

# Define task function
async def extract_emails(inputs: EmailInput) -> EmailOutput:
    """Task function that runs our agent."""
    result = await agent.run(inputs.text)
    return result.data

# Run evaluation
async def evaluate_email_extraction():
    """Run the full evaluation suite."""
    report = await dataset.evaluate(
        extract_emails,
        max_concurrency=5  # Run up to 5 cases in parallel
    )

    # Analyze results
    print(f"Cases evaluated: {len(report.results)}")
    print(f"All passed: {report.all_passed}")
    print(f"Pass rate: {report.pass_rate:.2%}")

    # Detailed results
    for result in report.results:
        print(f"\n{result.case_name}:")
        print(f"  Passed: {result.passed}")
        for eval_name, eval_result in result.evaluations.items():
            print(f"  {eval_name}: {eval_result.value}")
            if eval_result.reason:
                print(f"    Reason: {eval_result.reason}")

    # Save report
    with open('results/evaluation_report.json', 'w') as f:
        json.dump(report.model_dump(), f, indent=2)

    return report

# Run the evaluation
if __name__ == "__main__":
    import asyncio
    asyncio.run(evaluate_email_extraction())
```

### Running the Example

```bash
# Install dependencies
uv add pydantic-ai logfire

# Run evaluation
uv run python eval_email_extraction.py

# View results
cat results/evaluation_report.json
```

---

## Quick Reference

### Common Workflow

```python
# 1. Create cases
cases = [
    Case(name='test1', inputs={...}, expected_output=..., metadata={...}),
    Case(name='test2', inputs={...}, expected_output=..., metadata={...})
]

# 2. Choose evaluators
evaluators = [
    MaxDuration(duration=2.0),  # Performance
    EqualsExpected(),  # Correctness
    LLMJudge(rubric="..."),  # Quality
    MyCustomEvaluator()  # Domain-specific
]

# 3. Create dataset
dataset = Dataset(name='my_tests', cases=cases, evaluators=evaluators)

# 4. Run evaluation
async def my_task(inputs):
    # Your AI system logic
    return result

report = await dataset.evaluate(my_task)

# 5. Analyze results
print(f"Pass rate: {report.pass_rate:.2%}")
```

### Evaluator Selection Guide

| Need | Use This |
|------|----------|
| Exact match | `EqualsExpected()` |
| Contains text | `Contains(value="...")` |
| Type checking | `IsInstance(type_name="...")` |
| Performance | `MaxDuration(duration=...)` |
| Subjective quality | `LLMJudge(rubric="...")` |
| Agent behavior | `HasMatchingSpan(query={...})` |
| Custom logic | Create custom `Evaluator` |

---

## Additional Resources

- **Core Concepts**: https://ai.pydantic.dev/evals/core-concepts/
- **Cases & Datasets API**: https://ai.pydantic.dev/api/pydantic_evals/dataset/
- **Evaluators Overview**: https://ai.pydantic.dev/evals/evaluators/overview/
- **Evaluator API**: https://ai.pydantic.dev/api/pydantic_evals/evaluators/
- **Built-in Evaluators**: https://ai.pydantic.dev/evals/evaluators/built-in/
- **LLM Judge**: https://ai.pydantic.dev/evals/evaluators/llm-judge/
- **Custom Evaluators**: https://ai.pydantic.dev/evals/evaluators/custom/
- **Span-Based Evaluators**: https://ai.pydantic.dev/evals/evaluators/span-based/
- **Dataset Management**: https://ai.pydantic.dev/evals/how-to/dataset-management/

---

**Happy evaluating! 🚀**
