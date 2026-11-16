from task_operator.brain import new_client


def test_new_client_uses_key_from_config():
    """The API client gets its key from config, not from a function argument.
    (Creating a client makes no network call.)"""
    assert new_client().api_key == "sk-test-not-a-real-key"
