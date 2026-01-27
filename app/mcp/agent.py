from langchain.agents import initialize_agent
from langchain.tools import Tool
from app.mcp.tools import convert_tool, parse_tool
from app.rag.embeddings import get_llm

llm = get_llm()

tools = [
    Tool(
        name="convert_image",
        func=convert_tool,
        description="Convert an image to grayscale. Requires arguments: filename (string), filepath (string)"
    ),
    Tool(
        name="parse_page",
        func=parse_tool,
        description="Parse images from a webpage and process them"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    handle_parsing_errors=True
)

def run_agent(query: str):
    return agent.run(query)