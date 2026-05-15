from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup


load_dotenv()

llm = ChatOpenAI(model = "gpt-4o")

# Step 2 - define a tool
@tool
def say_hello(name: str) -> str:
    """Say hellp to someone by name"""
    return f"Hello {name}!"
@tool
def get_testcrunch_news(query: str) -> str:
    """Fetches the latest AI news from TestCrunch"""
    page = requests.get("https://techcrunch.com/category/artificial-intelligence/",
            headers = {"User-Agent": "Modzilla/5.0"}
        )
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.get_text()[:5000]
#Step 3- the prompt
# agent_scratchpad is where LangChain tracks tool calls internally
prompt = ChatPromptTemplate.from_messages([
    ("System", "You are a helpful assistant that can greet people and fetch AI news"),
    ("User", "{input}"),
    ("Placeholder", "{agent_scratchpad}")
])


# Step 4 - create the agent (the brain that decides which tools to use)
agent = create_openai_functions_agent(
    llm = llm,
    tools = [say_hello, get_testcrunch_news],
    prompt = prompt
)


# Step 5 - create the executor (the thing that actually runs it)
executor = AgentExecutor(
    agent = agent,
    tools = [say_hello, get_testcrunch_news],
    verbose = True    #SHows what the agent is thinking
)
result = executor.invoke({"input": "Say hello to John"})
print(result["output"])

result = executor.invoke({"input": "Get me the latest AI news"})
print(result["output"])