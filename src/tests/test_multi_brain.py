from agent.agent import Agent
from brain import BRAINS
from brain.fake_brain import FakeBrain


def test_agent_stores_brain_name(): 
    """Verify agent stores the brain name.""" 
    agent = Agent(brain=FakeBrain(), brain_name="claude") 
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
        agent = Agent(brain=FakeBrain(), brain_name="claude")
        result = agent.handle_input("/switch")
        assert "deepseek" in result
        assert agent.brain_name == "deepseek"
    finally:
        BRAINS.clear()
        BRAINS.update(original_brains)