from langchain.agents import initialize_agent
from langchain.tools import Tool
from app.mcp.tools import convert_tool, parse_tool
from app.rag.embeddings import get_llm

llm = get_llm()

def convert_image_wrapper(query: str):
    try:
        filename, filepath = query.split("|")
    except ValueError:
        return "Invalid format. Use 'filename|filepath'."
    return convert_tool(filename, filepath)

def parse_page_wrapper(query: str):
    return parse_tool(job_id="agent-job", url=query, limit=5)

tools = [
    Tool(
        name="convert_image",
        func=convert_image_wrapper,
        description="Convert an image to grayscale. Input format: 'filename|filepath'"
    ),
    Tool(
        name="parse_page",
        func=parse_page_wrapper,
        description="Parse images from a webpage. Input: URL string"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    handle_parsing_errors=True,
    verbose=True
)

def run_agent(query: str):
    return agent.invoke(query)