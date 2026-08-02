import os
import pytest
import requests
import json
from dotenv import load_dotenv

import tempfile
from src.tools import ReadFile, WriteFile, Thought, ToolCall, tools, ToolContext, SaveMemory

from src.agent import Agent
from src.brain import FakeBrain, BRAINS
from src.memory import Memory

##########################################
# Test API
##########################################

# 1. load the vault
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Basic check so we don't crash with a confusing "NoneType" error if the key isn't set
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")


# 2. Define the target
url = "https://api.anthropic.com/v1/messages"

# 3. Authenticate
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# 4. Construct the payload
payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": "Hello, are you ready to code?"
        }
    ]
}

# 5. Fire! (No safety net)
print("Sending request to Anthropic API...")
response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)

# 6. Inspect the raw response
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    # Successful response, parse the JSON
    response_data = response.json()
    print("Response JSON:")
    print(json.dumps(response_data, indent=4))
else:
    # Error response, print the error message
    print("Error response:")
    try:
        error_data = response.json()
        print(json.dumps(error_data, indent=4))
    except json.JSONDecodeError:
        print(response.text)



##########################################
# Test Tools
##########################################

# Read Tool Tests
def test_tool_has_required_attributes():
    """Verify tool classes have name, description, input_schema."""
    tool = ReadFile()
    assert tool.name == "read_file"
    assert tool.description is not None
    assert tool.input_schema is not None


def test_read_file_adds_line_numbers():
    """Verify ReadFile prefixes each line with line numbers."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt' , delete=False) as tmp_file:
        tmp_file.write("line one\nline two\nline three")
        tmp_file_path = tmp_file.name

    try:
        tool = ReadFile()
        result = tool.execute(ToolContext(), tmp_file_path)
        assert "1 | line one" in result
        assert "2 | line two" in result
        assert "3 | line three" in result
    finally:
        os.unlink(tmp_file_path)  # Clean up the temporary file

# Write Tool Tests
def test_write_file_creates_file():
    """Verify WriteFile creates a file with content."""
    with tempfile.TemporaryDirectory() as tmpdir:

        file_path = os.path.join(tmpdir, "test.txt")

        tool = WriteFile()
        result = tool.execute(ToolContext(), file_path, "Hello, World!")

        assert os.path.exists(file_path)
        assert "Successfully wrote" in result

        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == "Hello, World!"


# Memory tools test
def test_save_memory_updates_memory():
    """Verify SaveMemory updates the Memory object."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = Memory(path=os.path.join(tmpdir, "memory.md"))
        tool = SaveMemory()
        context = ToolContext(memory=memory)

        result = tool.execute(context, "Updated Preferences")

        assert "successfully" in result.lower()
        assert memory.content == "Updated Preferences"



#########################################################################
# Tests for the FakeBrain class
#########################################################################

# Test 1: The brain returns a response
def test_handle_input_returns_brain_response():
    """Verify handle_input returns the brain's response test."""

    brain = FakeBrain(responses=[Thought(text="Hello from FakeBrain!")])
    agent = Agent(brain=brain, tools=[])
    result = agent.handle_input("Hello, Agent!")
    assert result == "Hello from FakeBrain!"

# Test 2: Conversation accumulates
def test_conversation_accumulates():
    """Verify conversation list grows with each interaction."""
    brain = FakeBrain(responses=[
        Thought(text="Response 1"),
        Thought(text="Response 2"),
    ])

    agent = Agent(brain=brain, tools=[])
    agent.handle_input("First message")
    # Each input adds user and agent messages
    assert len(agent.conversation) == 2

    agent.handle_input("Second message")
    assert len(agent.conversation) == 4  


# Test 3: Correct message structure
def test_conversation_contains_correct_roles():
    """Verify that the conversation contains messages with correct roles."""
    brain = FakeBrain(responses=[Thought(
        text="AI Response",
        raw_content=[{"type": "text", "text": "AI Response"}]
    )])
    agent = Agent(brain=brain, tools=[])
    agent.handle_input("User message")

    # Check the last two messages in the conversation
    user_message = agent.conversation[-2]
    agent_message = agent.conversation[-1]

    assert user_message["role"] == "user"
    assert user_message["content"] == "User message"

    assert agent_message["role"] == "assistant"
    # raw_content is stored as a list
    assert agent_message["content"][0]["text"] == "AI Response"


# Test 4: Brain receives the conversation
def test_brain_receives_conversation():
    """Verify brain.think is called with the conversation list."""
    brain = FakeBrain()
    agent = Agent(brain=brain, tools=[])

    agent.handle_input("Test message")

    # The brain should have received the conversation
    assert brain.last_conversation is not None
    assert len(brain.last_conversation) == 1 
    assert brain.last_conversation[0]["role"] == "user"
    assert brain.last_conversation[0]["content"] == "Test message"





##########################################
# Test Multi Brain
##########################################

def test_agent_stores_brain_name(): 
    """Verify agent stores the brain name.""" 
    agent = Agent(brain=FakeBrain(), tools=[], brain_name="claude") 
    assert agent.brain_name == "claude" 

def test_brains_registry_has_expected_providers(): 
    """Verify BRAINS registry contains expected providers.""" 
    assert "claude" in BRAINS
    assert "deepseek" in BRAINS


def test_switch_command_toggles_brain_name():
    """Verify /switch updates brain_name."""
    # Mock BRAINS to use FakeBrain for switching
    original_brains = BRAINS.copy()
    BRAINS["claude"] = FakeBrain
    BRAINS["deepseek"] = FakeBrain

    try:
        agent = Agent(brain=FakeBrain(), tools=[], brain_name="claude")
        result = agent.handle_input("/switch")
        assert "deepseek" in result
        assert agent.brain_name == "deepseek"
    finally:
        BRAINS.clear()
        BRAINS.update(original_brains)




##########################################
# Test Agentic Loop
##########################################

def test_agentic_loop_executes_tool_calls():
    """Verify agentic loop executes tool calls and continues."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test content\n")
        temp_path = f.name

    try:
        # Brain returns a tool call, then a final response
        brain = FakeBrain(responses=[
            Thought(
                text="Let me read that file.",
                tool_calls=[ToolCall(id="1", tool_name="read_file", args={"path": temp_path})],
                raw_content=[
                    {"type": "text", "text": "Let me read that file."},
                    {"type": "tool_use", "id": "1", "name": "read_file", "input": {"path": temp_path}}
                ]
            ),
            Thought(
                text="The file contains test content.",
                raw_content=[{"type": "text", "text": "The file contains test content."}]
            )
        ])
        agent = Agent(brain=brain, tools=tools)
        result = agent.handle_input("Read the file")

        assert "Let me read that file." in result
        assert "The file contains test content." in result
        assert brain.call_count == 2  # Called twice (tool call + final)
    finally:
        os.unlink(temp_path)



#########################################################
# Test Memory
#########################################################

def test_memory_creates_default_file():
    """Verify Memory creates file with default content if missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "memory.md")
        memory = Memory(path=path)

        assert os.path.exists(path)
        assert "Coding Agent" in memory.content


def test_memory_save_updates_content_and_file():
    """Verify Memory.save() updates both content and file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "memory.md")
        memory = Memory(path=path)

        memory.save("New Content")

        assert memory.content == "New Content"
        with open(path) as f:
            assert f.read() == "New Content"
