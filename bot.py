from fastmcp import FastMCP
from ollama import Client
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Initialize MCP server
mcp = FastMCP(name="Blog_agent")

# Initialize Ollama client
ollama_client = Client()

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
 
BLOCKED_DOMAINS = ["medium.com", "youtube.com", "twitter.com", "reddit.com"]


class Docs:

    @staticmethod
    def summarize(query: str) -> str:
        """
        Summarizes the given query using local Ollama model.
        """
        messages = [
            {"role": "user", "content": f"Summarize this query in 2-3 sentences with context: {query}"}
        ]
        parts = []
        for part in ollama_client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
            parts.append(part["message"]["content"])
        return ''.join(parts).strip()

    @staticmethod
    def make_search_query(query: str) -> str:
        """
        Condenses a query into a short search string (under 400 chars).
        """
        messages = [
            {
                "role": "user",
                "content": (
                    f"Convert this into a short web search query under 10 words. "
                    f"Return only the search query, nothing else: {query}"
                )
            }
        ]
        parts = []
        for part in ollama_client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
            parts.append(part["message"]["content"])
        return ''.join(parts).strip()[:400]

    @staticmethod
    def search_web(query: str, search_depth: str = "advanced", top_k: int = None) -> list:
        """
        Use Tavily API to get search results.
        """
        try:
            client = TavilyClient(TAVILY_API_KEY)
            response = client.search(query=query, search_depth=search_depth)
            results = [item.get("url") for item in response.get("results", []) if "url" in item]
            return results[:top_k] if top_k else results
        except Exception as e:
            print(f"Tavily search failed: {e}")
            return []

    @staticmethod
    def fetch_docs(urls: list) -> list:
        """
        Fetch and clean text from URLs, skipping blocked domains.
        """
        docs = []
        for url in urls:
            if any(domain in url for domain in BLOCKED_DOMAINS):
                print(f"Skipping blocked domain: {url}")
                continue
            try:
                response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
                text = "\n".join(line for line in lines if line)
                docs.append(text[:3000])
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
        return docs

    @staticmethod
    def uni_function(query: str, top_k: int = 3) -> dict:
        """
        Full pipeline: Summarize → Search → Fetch → Answer
        """
        # Step 1: Summarize the query (for context/display)
        summary = Docs.summarize(query)

        # Step 2: Generate a short search query
        search_query = Docs.make_search_query(query)

        # Step 3: Search the web
        urls = Docs.search_web(search_query, top_k=top_k)

        # Step 4: Fetch and clean content from URLs
        docs = Docs.fetch_docs(urls)

        # Step 5: Generate grounded answer from fetched docs
        context = "\n\n---\n\n".join(docs)
        messages = [
            {
                "role": "user",
                "content": (
                    f"Using the following documentation, answer this query: {query}\n\n"
                    f"Documentation:\n{context}"
                )
            }
        ]
        answer_parts = []
        for part in ollama_client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
            answer_parts.append(part["message"]["content"])

        return {
            "query": query,
            "summary": summary,
            "search_query": search_query,
            "search_results": urls,
            "docs_fetched": len(docs),
            "answer": ''.join(answer_parts).strip()
        }


@mcp.tool()
def research(query: str, top_k: int = 3) -> dict:
    """
    Research a query by searching the web and returning a grounded answer.
    """
    return Docs.uni_function(query, top_k=top_k)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test query: python test.py test
        query = "How do I handle file uploads in Next.js 14?"
        output = Docs.uni_function(query)
        print(f"Query:        {output['query']}")
        print(f"Search Query: {output['search_query']}")
        print(f"Summary:      {output['summary']}")
        print(f"URLs:         {output['search_results']}")
        print(f"Docs fetched: {output['docs_fetched']}")
        print(f"Answer:\n{output['answer']}")
    else:
        # Default: start MCP server: python test.py
        mcp.run()