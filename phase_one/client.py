from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
import os
import sys
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def get_model():
    api_key = "Your API"

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=api_key,
        temperature=0.7,
        max_tokens=2000,
    )

llm = get_model()


server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

tests = [

    "list files in the current directory",
    "create a file called hello.txt with content Hello World",
    "read the file hello.txt",
    "show me system information",

    "create a table in sqlite",
    "insert a user John with age 25",
    "insert a user Alice with age 30",
    "get all users",
    "what is the current server time",
]


async def run():

    @retry(
        # Retry only on quota errors
        retry=retry_if_exception_type(ResourceExhausted),
        # Exponential backoff
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(3),  # Give up after 5 retries
        reraise=True
    )
    async def safe_ainvoke(agent, query, sleep_time: int = 2):
        await asyncio.sleep(sleep_time)  # Sleep before sending the query
        return await agent.ainvoke({"messages": query})

    async with stdio_client(server=server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            try:
                await session.initialize()
            except TimeoutError:
                print("Timeout: Server did not respond in time")

            try:
                tools = await load_mcp_tools(session=session)
            except Exception as e:
                print("Tools did not load:", e)
                tools = []

            agent = create_react_agent(llm, tools=tools)

            while True:
                query = input("\nQuery: ").strip()

                if query.lower() in ["exit", "quit"]:
                    break

                for query in tests:
                    print("\n==========User=============")
                    print(query)
                    import time

                    time.sleep(5)
                    response = await safe_ainvoke(agent, query)

                    try:
                        for msg in response['messages']:
                            if isinstance(msg, AIMessage):
                                print("==========AI=============")

                                print(msg.content)
                            elif isinstance(msg, HumanMessage):
                                pass
                            elif isinstance(msg, ToolMessage):
                                print("==========Tool=============")
                                print(f"(Tool message) {msg.content}")
                            else:
                                print(str(msg))
                    except Exception as e:
                        print("Error reading response:", e)
                        print(response)

if __name__ == "__main__":
    asyncio.run(run())
