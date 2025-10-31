BEST WAY TO BE THE BEST IS TO BECOME A FAST AND EFFECTIVE PROTOTYPER.

METRIC: X EXPERIMENTS PER DAY

# Notes

## Good

1. SQL search for the traces and span
2. Span level evals
3. Tracing seems automatic (gotta check out a bit more)
4. EU server instance
5. They are SOC 2 Type II, HIPAA and GDPR compliant.

## Bad

1. Pydantic Logfire has not sampling LLM Judge monitoring capabilities

## Good learnings

1. [Metrics & Attributes](https://ai.pydantic.dev/evals/how-to/metrics-attributes/#anti-pattern-duplicate-configuration) has good documentation on best practices how to use Logfire. Look at `Synchronization between Tasks and Experiment Metadata > Pattern 2: Configuration Object (Recommended)
`
2. [UI Event streams > Vercel AI](https://ai.pydantic.dev/ui/vercel-ai/) shows that Pydantic AI natively assaults the Vercel AI data-stream protocol to receive agent-run input from and stream events to a Vercel AI element frontend. Very important and just what I need.

## What to focus on

1. Priority should be on the evals instrumentation. Cuz that is my bread and butter.
2. For evals, as it is code-first and flexible, need to focus on:
   - How to instrument my code files to store datasets, experiment results, prompt management and also tracking metrics.
   - Using it to rapidly prototype AI configurations
3. Look at how Jason Liu (RAG) is using Pydantic Evals + Logfire to run experiments and analyse results.
4. Main goal is to solidify my mental model on using Pydantic AI + Evals + Logfire as my AI prototyping stack.
