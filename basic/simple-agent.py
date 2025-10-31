import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from rich import print

load_dotenv()
logfire.configure()
logfire.instrument_pydantic_ai()

model_settings = OpenAIResponsesModelSettings(
    openai_text_verbosity="low", openai_reasoning_generate_summary="detailed"
)
model = OpenAIResponsesModel("gpt-5-nano-2025-08-07")
# strangely I cannot set the reasoning to concise. Keeps returning the error that it doesnt exist.

agent = Agent(
    model=model,
    model_settings=model_settings,
    instructions="""help the student understand more about the country asked""",
    system_prompt="""You are an experienced geography teacher""",
)

result = agent.run_sync("What is the capital of Italy?")
print(result.all_messages())
