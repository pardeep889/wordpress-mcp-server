import asyncio
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import markdown2

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define a system instruction
SYSTEM_PROMPT = (
    "You are an intelligent agent capable of interacting with WooCommerce and WordPress APIs. "
    "Your tasks include managing products, orders, and customer information. "
    "You can invoke tools when needed to accomplish these tasks.\n"
    "Exract data from the user's message(turn into proper format which can be used by tools or apis of wordpress and woo commerce) and use the following credentials to invoke tools:\n"
    "use following credentials:\n"
    f"WOCOMMERCE_CONSUMER_KEY: {os.getenv('WOCOMMERCE_CONSUMER_KEY')}\n"
    f"WOCOMMERCE_CONSUMER_SECRET: {os.getenv('WOCOMMERCE_CONSUMER_SECRET')}\n"
    f"WORDPRESS_SITE_URL: {os.getenv('WORDPRESS_SITE_URL')}\n"
    f"WORDPRESS_JWT_TOKEN: {os.getenv('WORDPRESS_JWT_TOKEN')}\n"
)

@app.on_event("startup")
async def startup_event():
    global agent
    config = {
        "mcpServers": {
            "wordpress_mcp_server": {
                "command": "python3",
                "args": ["/Users/xpertdev/Desktop/Pardeep/mcp-server-wordpress/server.py"],
                "env": {
                    "WORDPRESS_SITE_URL": os.getenv("WORDPRESS_SITE_URL"),
                    "WORDPRESS_JWT_TOKEN": os.getenv("WORDPRESS_JWT_TOKEN"),
                    "WOCOMMERCE_CONSUMER_KEY": os.getenv("WOCOMMERCE_CONSUMER_KEY"),
                    "WOCOMMERCE_CONSUMER_SECRET": os.getenv("WOCOMMERCE_CONSUMER_SECRET"),
                },
            }
        }
    }
    client = MCPClient.from_dict(config)
    llm = ChatOpenAI(model="gpt-4o")  # Keep the raw ChatOpenAI model
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "response": ""})

@app.post("/chat", response_class=HTMLResponse)
async def post_chat(request: Request, message: str = Form(...)):
    # Prepend the system prompt to the user's message
    prompt_with_context = f"{SYSTEM_PROMPT}\nUser: {message}"
    print("Prompt sent to agent:\n", prompt_with_context)
    raw_result = await agent.run(prompt_with_context)
    html_result = markdown2.markdown(raw_result)
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "response": html_result, "message": message}
    )
