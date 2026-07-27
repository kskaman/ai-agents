import pytest
from coding_agent import Agent, AgentStop, Thought

#########################################################################
# FakeBrain class to simulate LLM responses for testing purposes
#########################################################################

class FakeBrain:
    """A fake brain (generates LLM-like responses) that can be used for testing purposes."""

    def __init__(self, responses=None):
        self.responses = responses or [Thought(text="Fake response")]
        self.call_count = 0
        self.last_conversation = None

    def think(self, conversation):
        """Simulate thinking by returning a pre-defined response."""
        self.last_conversation = list(conversation)  # Store a copy of the conversation
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        return Thought(text="No more responses.")



#########################################################################
# Tests for the FakeBrain class
#########################################################################

# Test 1: The brain returns a response
def test_handle_input_returns_brain_response():
    """Verify handle_input returns the brain's response test."""

    brain = FakeBrain(responses=[Thought(text="Hello from FakeBrain!")])
    agent = Agent(brain=brain)
    result = agent.handle_input("Hello, Agent!")
    assert result == "Hello from FakeBrain!"

# Test 2: Conversation accumulates
def test_conversation_accumulates():
    """Verify conversation list grows with each interaction."""
    brain = FakeBrain(responses=[
        Thought(text="Response 1"),
        Thought(text="Response 2"),
    ])

    agent = Agent(brain=brain)
    agent.handle_input("First message")
    # Each input adds user and agent messages
    assert len(agent.conversation) == 2

    agent.handle_input("Second message")
    assert len(agent.conversation) == 4  


# Test 3: Correct message structure
def test_conversation_contains_correct_roles():
    """Verify that the conversation contains messages with correct roles."""
    brain = FakeBrain(responses=[Thought(text="AI Response")])
    agent = Agent(brain=brain)
    agent.handle_input("User message")

    # Check the last two messages in the conversation
    user_message = agent.conversation[-2]
    agent_message = agent.conversation[-1]

    assert user_message["role"] == "user"
    assert user_message["content"] == "User message"

    assert agent_message["role"] == "assistant"
    assert agent_message["content"] == "AI Response"


# Test 4: Brain receives the conversation
def test_brain_receives_conversation():
    """Verify brain.think is called with the conversation list."""
    brain = FakeBrain()
    agent = Agent(brain=brain)

    agent.handle_input("Test message")

    # The brain should have received the conversation
    assert brain.last_conversation is not None
    assert len(brain.last_conversation) == 1 
    assert brain.last_conversation[0]["role"] == "user"
    assert brain.last_conversation[0]["content"] == "Test message"