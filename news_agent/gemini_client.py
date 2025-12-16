import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# MCP Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Gemini Imports
from google import genai
from google.genai.types import (
    Content, 
    Part,
    Type,
    Tool,
    GenerateContentConfig,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format="[MCP_CLIENT] %(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Configure Gemini
try:
    GENAI_CLIENT = genai.Client()
except Exception as e:
    logger.error(f"Error initializing Google GenAI Client: {e}")
    sys.exit(1)

# --- Helper Function for Type Conversion ---
def map_type(json_type):
    """Maps JSON Schema types (used by MCP) to Gemini Parameter Types."""
    type_map = {
        "string": Type.STRING, 
        "integer": Type.INTEGER, 
        "boolean": Type.BOOLEAN
    }
    return type_map.get(json_type, Type.STRING)


def convert_mcp_to_gemini_tools(mcp_tools):
    """Converts MCP tool definitions into a list of Gemini-compatible function declarations."""

    gemini_funcs = []
    for tool in mcp_tools.tools:
        properties = {}
        for param_name, param_def in tool.inputSchema.get("properties", {}).items():
            logger.info(f"{param_name}, {param_def}")
            properties[param_name] = {
                "type": map_type(param_def.get("type", "string").lower()),
                "description": param_def.get("description", "")
            }
            if "enum" in param_def:
                raw_enum_values = param_def["enum"]
                filtered_enum_values = [enum_val for enum_val in raw_enum_values if enum_val]
                properties[param_name]["enum"] = filtered_enum_values
        
        gemini_funcs.append(
            Tool(
                function_declarations= [{
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                    }
                }]
            )
        )
    
    return gemini_funcs


async def run_interactive_chat(session, gemini_tools):
    """Runs interactive chat between the user, LLM, and MCP server."""
    logger.info(f"{gemini_tools=}")

    # --- Main Interaction Loop ---
    logger.info("\n✨ News Agent Started. Ask for the 'top K world events' or type 'quit'.\n")
    user_input = input("You: ")

    contents = [
        Content(parts=[Part(text=user_input)])
    ]
    remove_extraneous_contents = False
    
    while True:

        if user_input.lower() in ["quit", "exit"]:
            break

        # A. Send message to Gemini
        response = await GENAI_CLIENT.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=GenerateContentConfig(
                tools=gemini_tools,
            )
        )

        # B. Check if Gemini wants to call a function (Tool Use)
        if response.function_calls:
            logger.info("🤖 Model requested a tool call.")
            # Prepare the response parts for the function results
            responses_of_tool_calls = []

            for call in response.function_calls:
                func_name = call.name
                func_args = dict(call.args)
                logger.info(f"⚡ Gemini is executing tool: {func_name} with args: {func_args}")

                # C. Execute Tool on MCP Server
                try:
                    result = await session.call_tool(func_name, arguments=func_args)
                    tool_output = ""

                    for content in result.content:
                        if content.type == "text":
                            tool_output += content.text
                            tool_output += "\n"
                except Exception as e:
                    tool_output = f"Error executing tool via MCP: {e}"
                
                responses_of_tool_calls.append(
                    Part.from_function_response(
                        name=func_name,
                        response={"result": tool_output}
                    )
                )
            
            # D. Send Result Back to Gemini for final response
            contents.append(response.candidates[0].content) # Model's original request
            contents.append(Content(parts=responses_of_tool_calls)) # Tool output
            contents.append(
                Content(parts=[Part(
                    text="Distill the above news stories into precisely the number of news stories or events or themes specified previously by the user."
                )])
            )
            remove_extraneous_contents = True
        elif response.text:
            print("\n--- Answer ---\n")
            print(f"\nAI: {response.text}")

            # remove the tool response from the context to keep the context compact
            if remove_extraneous_contents is True:
                contents = contents[:-3]
                remove_extraneous_contents = False

            contents.append(response.candidates[0].content)

            user_input = input("You: ")
            contents.append(
                Content(parts=[Part(text=user_input)])
            )
        else:
            # Fallback for unexpected or empty responses
            logger.error("\n[INFO] Model returned no text and no tool call. Exiting.")
            break


async def run_gemini_client():
    # Start the MCP Server as a subprocess
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        env=None
    )

    logger.info("🔌 Starting MCP Server and connecting client...")

    try:
        # When the stdio_client successfully connects, 
        # it returns a tuple containing two asynchronous stream objects:
        # 1. read: An object used to read the output (JSON-RPC responses) from the server's stdout
        # 2. write: An object used to write commands (JSON-RPC requests) to the server's stdin
        async with stdio_client(server_params) as (read, write):
            # ClientSession(read, write) wraps the read and write streams in a high-level 
            # MCP session handler. It is responsible for translating Python method calls 
            # (like call_tool) into the formal JSON-RPC messages and vice-versa. All 
            # subsequent tool calls and requests are made through session object.
            async with ClientSession(read, write) as session:

                # initialize is the first official MCP message sent over the newly established streams. 
                # It sends a specific JSON-RPC request to server.py telling it to start its 
                # initialization routine. The server typically uses this time to check its API keys, 
                # load its internal resources, and prepare to expose its tools.
                await session.initialize()

                # Fetch and Convert Tools
                mcp_tools = await session.list_tools()
                gemini_tools = convert_mcp_to_gemini_tools(mcp_tools)

                logger.info(f"🛠️  Found {len(gemini_tools)} tool(s) for Gemini.")

                await run_interactive_chat(session, gemini_tools)
                print("👋 Bye!")

    except Exception as e:
        logger.exception(
            f"\nFATAL ERROR: Could not run the client or connect to the server. Check your dependencies and API keys. Error: {e}"
        )


if __name__ == "__main__":
    asyncio.run(run_gemini_client())


