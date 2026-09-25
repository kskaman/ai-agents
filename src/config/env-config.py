from dotenv import load_dotenv


load_dotenv()

def get_env_variable(name: str) -> str:
    """Retrieve an environment variable or raise an error if not found."""
    import os
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{name}' not found.")
    return value


env = {
    "ANTHROPIC_MODEL": get_env_variable("ANTHROPIC_MODEL"),
    "ANTHROPIC_API_KEY": get_env_variable("ANTHROPIC_API_KEY"),
    "OPENAI_MODEL": get_env_variable("OPENAI_MODEL"),
    "OPENAI_API_KEY": get_env_variable("OPENAI_API_KEY"),
}