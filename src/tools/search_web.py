import requests
from urllib.parse import urlencode


class SearchWeb:
    """Searches the web using DuckDuckGo."""

    name = "search_web"
    plan_safe = True
    description = "Searches the web using DuckDuckGo and returns a list of" \
        " relevant results with titles, URLs, and snippets."

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default 5)."
            },
        },
        "required": ["query"]
    }

    DDGS_URL = "https://api.duckduckgo.com/"

    def execute(self, context, query, max_results=5):
        print(f"  -> Searching the web for '{query}'")

        try:
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1",
            }

            response = requests.get(
                self.DDGS_URL,
                params=params,
                headers={"User-Agent": "coding-agent/1.0"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            results = []

            # Instant answer / abstract
            if data.get("AbstractText"):
                results.append(
                    f"Summary: {data['AbstractText']}\n"
                    f"Source:  {data.get('AbstractURL', '')}"
                )

            # Related topics (the main DDG JSON result list)
            for topic in data.get("RelatedTopics", []):
                if len(results) >= max_results:
                    break

                # Topics can be nested under a "Topics" key (sub-categories)
                if "Topics" in topic:
                    for sub in topic["Topics"]:
                        if len(results) >= max_results:
                            break
                        entry = self._format_topic(sub)
                        if entry:
                            results.append(entry)
                else:
                    entry = self._format_topic(topic)
                    if entry:
                        results.append(entry)

            if not results:
                return (
                    f"No results found for '{query}'. "
                    "Try rephrasing your query."
                )

            return "\n\n".join(results)

        except requests.exceptions.Timeout:
            return "Error: The search request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Error performing web search: {e}"
        except Exception as e:
            return f"Unexpected error during web search: {e}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _format_topic(self, topic: dict) -> str:
        """Format a single RelatedTopic dict into a readable string."""
        text = topic.get("Text", "").strip()
        url = topic.get("FirstURL", "").strip()
        if not text:
            return ""
        if url:
            return f"{text}\nURL: {url}"
        return text
