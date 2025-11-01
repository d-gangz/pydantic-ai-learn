"""
AI agent with file system access and bash command execution capabilities.

Input data sources: User prompts, local file system
Output destinations: Console output, local file system
Dependencies: pydantic-ai, subprocess, pathlib
Key exports: agent, run_bash_command(), read_file(), write_file()
Side effects: Executes bash commands, reads/writes files
"""

import subprocess
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()


def run_bash_command(command: str) -> str:
    """
    Execute a bash command and return its output.

    Args:
        command: The bash command to execute

    Returns:
        Combined stdout and stderr output
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout for safety
        )

        output = []
        if result.stdout:
            output.append(f"stdout:\n{result.stdout}")
        if result.stderr:
            output.append(f"stderr:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Return code: {result.returncode}")

        return (
            "\n".join(output) if output else "Command executed successfully (no output)"
        )

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        return path.read_text()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_directory(directory_path: str = ".") -> str:
    """
    List contents of a directory.

    Args:
        directory_path: Path to the directory (defaults to current directory)

    Returns:
        Directory listing or error message
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory '{directory_path}' does not exist"
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory"

        items = []
        for item in sorted(path.iterdir()):
            item_type = "DIR " if item.is_dir() else "FILE"
            items.append(f"{item_type} {item.name}")

        return "\n".join(items) if items else "Directory is empty"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Create the agent with all tools
agent = Agent(
    "openai:gpt-4",
    tools=[run_bash_command, read_file, write_file, list_directory],
    system_prompt="""You are a helpful AI assistant with access to the local file system and bash commands.

You can:
- Execute bash commands using run_bash_command()
- Read files using read_file()
- Write files using write_file()
- List directory contents using list_directory()

Important safety guidelines:
- Always explain what you're about to do before executing commands
- Be cautious with destructive operations (rm, mv, etc.)
- Validate file paths before reading/writing
- Use relative paths when possible for portability

When the user asks you to do something, think through the steps and use the appropriate tools to accomplish the task.
""",
)


def main():
    """Run the agent in interactive mode."""
    print("🤖 AI Agent with File System Access")
    print("=" * 50)
    print("I can help you with file operations and bash commands.")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break

            if not user_input:
                continue

            # Run the agent
            result = agent.run_sync(user_input)
            print(f"\nAgent: {result.output}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
