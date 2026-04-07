import os
from dotenv import load_dotenv
from ddgs import DDGS
import arxiv
import wikipediaapi
from agents import function_tool, Agent, ModelSettings, set_tracing_disabled
from openai import AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# Load environment variables
load_dotenv()

# Disable tracing for local runs
set_tracing_disabled(True)

# Model configuration
base_url = os.getenv("BASE_URL", "http://localhost:11434/v1")
model_key = os.getenv("MODEL_KEY", "ollama")
model_name = os.getenv("MODEL_NAME", "minimax-m2.5:cloud")

# Initialize client and model
client = AsyncOpenAI(
    base_url=base_url,
    api_key=model_key
)

ollama_model = OpenAIChatCompletionsModel(
    model=model_name,
    openai_client=client
)

# Tool definitions
@function_tool
def web_search(query: str, region: str = "wt-wt", safesearch: str = "moderate", time: str = "m", max_results: int = 5):
    """
    Perform a web search for the latest information.
    """
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, region=region, safesearch=safesearch, timelimit=time, max_results=max_results)]
        return results

@function_tool
def arxiv_search(query: str, max_results: int = 5):
    """
    Search for scientific papers on ArXiv.
    """
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for result in client.results(search):
        results.append({
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary,
            "url": result.entry_id
        })
    return results

@function_tool
def wikipedia_search(query: str):
    """
    Search and get the summary of a Wikipedia page.
    """
    wiki = wikipediaapi.Wikipedia('ResearchAgent/1.0 (contact: researcher@example.com)', 'en')
    page = wiki.page(query)
    if page.exists():
        return {"title": page.title, "summary": page.summary[:2000], "full_url": page.fullurl}
    return f"No Wikipedia page found for '{query}'."

# Research Agent Definition
research_agent = Agent(
  name="Research Agent",
  instructions="You are a Research Agent. Use the web search, arxiv_search, and wikipedia_search tools to provide comprehensive research on any topic. Reply short and don't use markdown just text., REPLY SHORT AS POSSIBLE",
  model=ollama_model,
  tools=[web_search, arxiv_search, wikipedia_search],
  model_settings=ModelSettings(
    temperature=0.7,
    parallel_tool_calls=True,
    max_tokens=4096,
  )
)
