"""
Demonstrates Logfire tracing with Pydantic AI agents in a multi-step workflow.

Input data sources: User prompt for story generation
Output destinations: Console output (story text)
Dependencies: OpenAI API key in .env, Logfire configuration
Key exports: main(), delay_one_second()
Side effects: Makes OpenAI API calls, sends traces to Logfire
"""
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

load_dotenv()
logfire.configure()
logfire.instrument_pydantic_ai()

model_settings = OpenAIResponsesModelSettings(
    openai_text_verbosity="low", openai_reasoning_generate_summary="detailed"
)
model = OpenAIResponsesModel("gpt-5-nano-2025-08-07")
# strangely I cannot set the reasoning to concise. Keeps returning the error that it doesnt exist.


class Story(BaseModel):
    outline: str = Field(description="The outline of the story")
    reasoning: str = Field(description="The reasoning behind the outline")


outline_agent = Agent(
    model=model,
    model_settings=model_settings,
    instructions="""Based on the user's request, create a simple outline for a story.""",
    output_type=Story,
)

write_story_agent = Agent(
    model=model,
    model_settings=model_settings,
    instructions="""Based on the given outline, write a short story less than 100 words.""",
)


@logfire.instrument("delay_one_second")
def delay_one_second() -> None:
    """Sleep for one second."""
    import time

    time.sleep(1)


def main() -> None:
    """Main function to orchestrate the story generation workflow."""
    with logfire.span("story_generation_workflow", user_name="Wukee"):
        # Step 1: Generate the outline
        outline_result = outline_agent.run_sync("What is the capital of Italy?")
        # Step 2: Wait one second
        delay_one_second()
        # Step 3: Write the story based on the outline
        story_result = write_story_agent.run_sync(outline_result.output.outline)
        return story_result.output


if __name__ == "__main__":
    main()
