# Pydantic AI Tracing with Logfire

## Key Learnings

### 1. Wrapping Workflows with `logfire.span()`

**Problem**: Without `logfire.span()` in the main function, Logfire doesn't create a parent span that wraps the entire workflow. You only see individual agent runs (like `outline_agent` and `write_story_agent`) as separate traces.

**Solution**: Use `logfire.span()` to group related operations:

```python
def main() -> None:
    with logfire.span("story_generation_workflow"):
        outline_result = outline_agent.run_sync("What is the capital of Italy?")
        delay_one_second()
        story_result = write_story_agent.run_sync(outline_result.output.outline)
        return story_result.output
```

This creates a parent span that wraps all operations, making it easy to see the complete workflow hierarchy.

### 2. Tracing Custom Functions with `@logfire.instrument()`

**Problem**: Custom functions (like `delay_one_second()`) aren't automatically traced by Logfire, even when called within a traced workflow.

**Solution**: Add the `@logfire.instrument()` decorator with a custom name:

```python
@logfire.instrument("delay_one_second")
def delay_one_second() -> None:
    """Sleep for one second."""
    import time
    time.sleep(1)
```

**Important**: Without the name parameter, the span will show as something like `calling __main__delay_one_second` (based on the internal method name), which is not user-friendly. Always provide a descriptive name.

### 3. Adding Metadata to Traces

You can add custom metadata to your traces by passing attributes as keyword arguments to `logfire.span()`:

```python
with logfire.span("story_generation_workflow", user_name="Wukee", workflow_type="story_generation"):
    # your code here
```

This works just like when logging - any keyword arguments you pass will be attached as attributes to the span, making it easier to filter and analyze traces in Logfire.

### 4. Naming Services with `service_name`

**Problem**: When running multiple services or workflows, it can be hard to filter and identify traces in Logfire.

**Solution**: Use the `service_name` parameter in `logfire.configure()`:

```python
logfire.configure(service_name="story-generation-service")
```

This gives your service a meaningful name in the Logfire dashboard, making it easier to:
- Filter traces by service
- Organize logs when running multiple applications
- Support distributed tracing across multiple services

Example with different workflows:
```python
# In your story generation service
logfire.configure(service_name="story-generator")

# In your summarization service
logfire.configure(service_name="text-summarizer")
```

### 5. Basic Setup

```python
import logfire
from dotenv import load_dotenv

load_dotenv()
logfire.configure(service_name="my-service")  # Name your service
logfire.instrument_pydantic_ai()  # Auto-instrument Pydantic AI agent runs
```

## Reference

- [Logfire Manual Tracing Guide](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/add-manual-tracing/#convenient-function-spans-with-logfireinstrument)
- [Logfire API Reference - configure()](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.logfire_info)
