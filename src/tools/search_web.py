try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


class SearchWeb:
    """Searches the internet using DuckDuckGo."""

    name = "search_web"
    plan_safe = True
    description = (
        "Searches the internet for current information. "
        "Use when you need knowledge beyond your training data."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    }

    def execute(self, context, query):
        print(f"  -> Searching web for '{query}'")
        if DDGS is None:
            return "Error: ddgs package not installed. Run: pip install ddgs"

        try:
            results = DDGS().text(query, max_results=3)
            if not results:
                return "No results found."

            formatted = []
            for result in results:
                formatted.append(
                    f"Title: {result['title']}\n"
                    f"URL: {result['href']}\n"
                    f"Summary: {result['body']}\n"
                )

            return "\n".join(formatted)
        except Exception as e:
            return f"Error searching web: {e}"
