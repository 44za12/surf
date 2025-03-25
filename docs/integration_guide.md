# SURF Integration Guide

This guide provides detailed instructions for integrating SURF API with various LLM systems and frameworks.

## Table of Contents

- [Basic Integration Concepts](#basic-integration-concepts)
- [Integration with LangChain](#integration-with-langchain)
- [Integration with LlamaIndex](#integration-with-llamaindex)
- [Direct Integration with OpenAI API](#direct-integration-with-openai-api)
- [Integration with Hugging Face Transformers](#integration-with-hugging-face-transformers)
- [Integration with Model Context Protocol (MCP)](#integration-with-model-context-protocol-mcp)
- [Custom LLM Integration](#custom-llm-integration)
- [Troubleshooting](#troubleshooting)

## Basic Integration Concepts

SURF API provides two primary endpoints that can be used with any LLM system:

1. **Content Reading** (`/read/{url}`): Fetches and processes web content for LLM consumption
2. **Web Search** (`/search?q={query}`): Performs web searches and returns relevant results

The most common integration patterns are:

### 1. Tool-Based Integration

Configure SURF endpoints as tools that your LLM can use to access web information:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Read and process a webpage for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to read"
                    }
                },
                "required": ["url"]
            }
        }
    }
]
```

### 2. Retrieval Augmentation (RAG)

Use SURF as a retriever in a Retrieval-Augmented Generation system:

```python
def retrieve_from_web(query):
    # Search the web using SURF
    search_results = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "format": "json", "max_results": 3}
    ).json()
    
    # For each result, fetch the content
    documents = []
    for result in search_results["results"]:
        try:
            content = requests.get(
                f"http://localhost:8000/read/{result['url']}",
                params={"format": "json"}
            ).json()
            documents.append({
                "title": content["title"],
                "content": content["content"],
                "url": content["url"]
            })
        except Exception as e:
            print(f"Error retrieving {result['url']}: {e}")
    
    return documents
```

### 3. Direct Context Injection

Add web content directly into your prompts:

```python
def generate_response_with_web_info(user_query):
    # Search for relevant information
    search_results = requests.get(
        "http://localhost:8000/search",
        params={"q": user_query, "format": "json", "max_results": 2}
    ).json()
    
    # Create prompt with context
    prompt = f"""
    User query: {user_query}
    
    Relevant information from the web:
    
    """
    
    for i, result in enumerate(search_results["results"], 1):
        prompt += f"{i}. {result['title']} ({result['url']}): {result['snippet']}\n\n"
    
    prompt += "Based on the above information, please provide a comprehensive answer to the user's query."
    
    # Send to LLM
    response = llm.generate(prompt)
    return response
```

## Integration with LangChain

[LangChain](https://github.com/langchain-ai/langchain) is a popular framework for developing applications with LLMs. Here's how to integrate SURF:

### Creating Custom Tools

```python
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
import requests

# Define SURF tools
def search_web(query):
    """Search the web for information."""
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "format": "json", "max_results": 5}
    )
    return response.json()

def read_webpage(url):
    """Read and process a webpage."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    response = requests.get(
        f"http://localhost:8000/read/{url}",
        params={"format": "json"}
    )
    return response.json()

# Create LangChain tools
tools = [
    Tool(
        name="SearchWeb",
        func=search_web,
        description="Useful for searching the web for information on a topic. Input should be a search query."
    ),
    Tool(
        name="ReadWebpage",
        func=read_webpage,
        description="Useful for reading and extracting information from a webpage. Input should be a URL."
    )
]

# Initialize agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
result = agent.run("What are the latest developments in quantum computing?")
```

### Creating a Custom Retriever

```python
from langchain.retrievers import BaseRetriever
from langchain.schema import Document
import requests

class SURFRetriever(BaseRetriever):
    """Retriever that uses SURF to search the web."""
    
    def __init__(self, max_results=5):
        super().__init__()
        self.max_results = max_results
        
    def _get_relevant_documents(self, query):
        # Search for information
        search_results = requests.get(
            "http://localhost:8000/search",
            params={"q": query, "format": "json", "max_results": self.max_results}
        ).json()
        
        # Convert to documents
        documents = []
        for result in search_results["results"]:
            documents.append(
                Document(
                    page_content=result["snippet"],
                    metadata={"title": result["title"], "url": result["url"]}
                )
            )
            
        return documents
```

## Integration with LlamaIndex

[LlamaIndex](https://github.com/jerryjliu/llama_index) is a data framework for LLM applications. Here's how to integrate SURF:

### Creating a Custom Reader

```python
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
import requests

class SURFReader(BaseReader):
    """Reader that fetches web content using SURF."""
    
    def load_data(self, urls):
        """Load data from the given URLs."""
        documents = []
        
        for url in urls:
            try:
                response = requests.get(
                    f"http://localhost:8000/read/{url}",
                    params={"format": "json"}
                )
                data = response.json()
                
                documents.append(
                    Document(
                        text=data["content"],
                        metadata={
                            "title": data["title"],
                            "url": data["url"]
                        }
                    )
                )
            except Exception as e:
                print(f"Error loading {url}: {e}")
                
        return documents
```

### Creating a Custom Retriever

```python
from llama_index.retrievers import BaseRetriever
from llama_index.schema import NodeWithScore, QueryBundle
import requests

class SURFWebRetriever(BaseRetriever):
    """Retriever that searches the web using SURF."""
    
    def __init__(self, max_results=5):
        """Initialize the retriever."""
        self.max_results = max_results
        
    def _retrieve(self, query_bundle: QueryBundle):
        """Retrieve nodes given query."""
        search_results = requests.get(
            "http://localhost:8000/search",
            params={"q": query_bundle.query_str, "format": "json", "max_results": self.max_results}
        ).json()
        
        nodes = []
        for result in search_results["results"]:
            node = NodeWithScore(
                node=Node(
                    text=result["snippet"],
                    metadata={
                        "title": result["title"],
                        "url": result["url"]
                    }
                ),
                score=1.0 / (i + 1)  # Simple ranking based on position
            )
            nodes.append(node)
            
        return nodes
```

## Direct Integration with OpenAI API

### Function Calling with SURF

```python
import openai
import requests

# Set your OpenAI API key
openai.api_key = "your-api-key"

# Define functions for web access
functions = [
    {
        "name": "search_web",
        "description": "Search the web for information on a specific topic",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_webpage",
        "description": "Read and process a webpage",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to read"
                }
            },
            "required": ["url"]
        }
    }
]

# Function implementations
def search_web(query, max_results=5):
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "format": "json", "max_results": max_results}
    )
    return response.json()

def read_webpage(url):
    response = requests.get(
        f"http://localhost:8000/read/{url}",
        params={"format": "json"}
    )
    return response.json()

# Process user query
def process_query(user_query):
    messages = [{"role": "user", "content": user_query}]
    
    while True:
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        
        response_message = response["choices"][0]["message"]
        messages.append(response_message)
        
        # Check if function call is requested
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(response_message["function_call"]["arguments"])
            
            # Execute the function
            if function_name == "search_web":
                function_response = search_web(
                    function_args.get("query"),
                    function_args.get("max_results", 5)
                )
            elif function_name == "read_webpage":
                function_response = read_webpage(function_args.get("url"))
            else:
                function_response = {"error": "Function not found"}
                
            # Add function response to messages
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_response)
            })
        else:
            # Return the final response
            return response_message["content"]
```

## Integration with Hugging Face Transformers

### Using SURF with Hugging Face Pipeline

```python
from transformers import pipeline
import requests

def get_web_content(url):
    """Fetch content from a webpage using SURF."""
    response = requests.get(
        f"http://localhost:8000/read/{url}",
        params={"format": "json"}
    )
    return response.json()

# Initialize a summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Get web content and summarize it
def summarize_webpage(url):
    # Get content from SURF
    content = get_web_content(url)
    
    # Extract the text content
    text = content["content"]
    
    # Summarize in chunks if necessary (BART has a 1024 token limit)
    max_chunk_length = 1000
    chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summaries.append(summary[0]["summary_text"])
    
    return {
        "title": content["title"],
        "url": content["url"],
        "summary": " ".join(summaries)
    }
```

## Integration with Model Context Protocol (MCP)

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard developed by Anthropic that streamlines the integration of AI assistants with external data sources and tools. SURF can be implemented as an MCP server, allowing any MCP-compatible AI assistant to leverage its web search and content reading capabilities.

### Creating a SURF MCP Server

```python
from mcp import MCPServer, ServerSchema, RequestContext
import requests
import json

# Define the schema for your SURF MCP server
schema = ServerSchema(
    name="surf",
    description="Search utility and reading framework for web access",
    capabilities=[
        {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (1-10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "read_content",
            "description": "Fetch and process web content",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to read"
                    }
                },
                "required": ["url"]
            }
        }
    ]
)

# Define handler functions for each capability
async def search_web(context: RequestContext, params: dict):
    query = params.get("query")
    max_results = params.get("max_results", 5)
    
    # Call SURF API for search
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "format": "json", "max_results": max_results}
    )
    
    return response.json()

async def read_content(context: RequestContext, params: dict):
    url = params.get("url")
    
    # Call SURF API to read content
    response = requests.get(
        f"http://localhost:8000/read/{url}",
        params={"format": "json"}
    )
    
    return response.json()

# Create and start MCP server
server = MCPServer(schema=schema)
server.register_capability("search_web", search_web)
server.register_capability("read_content", read_content)

# Start the server
server.start()
```

### Using SURF with Anthropic's Claude

Claude Desktop application supports MCP integration. Once you have your SURF MCP server running:

1. Open Claude Desktop
2. Go to Settings > Model Context Protocol
3. Add your local SURF MCP server
4. Start a new conversation and use the SURF capabilities:

Example prompt:
```
Can you search for the latest news about quantum computing and summarize the key points?
```

When Claude recognizes it needs web information, it will use your SURF MCP server to search and retrieve content.

### Benefits of MCP Integration

- **Standardized Integration**: Connect SURF to any MCP-compatible AI assistant
- **Enhanced Context**: Provide AI models with up-to-date web information
- **Seamless User Experience**: Users interact naturally with the AI, which handles the web access behind the scenes
- **Future-proof**: Join the growing MCP ecosystem with hundreds of tools and data sources

### Creating Custom MCP Clients

You can create custom applications that leverage both SURF and MCP:

```python
from mcp import MCPClient
import asyncio

async def main():
    # Connect to SURF MCP server
    client = MCPClient("http://localhost:5000")
    
    # Call search capability
    search_results = await client.call(
        "search_web",
        {"query": "latest AI research", "max_results": 3}
    )
    
    # Process and display results
    for i, result in enumerate(search_results["results"], 1):
        print(f"{i}. {result['title']} - {result['url']}")
        
        # Get full content of the first result
        if i == 1:
            content = await client.call(
                "read_content",
                {"url": result['url']}
            )
            
            print(f"\nExcerpt from {content['title']}:\n")
            print(content['content'][:500] + "...\n")

asyncio.run(main())
```

## Custom LLM Integration

### Creating a Proxy API for Local LLMs

```python
from fastapi import FastAPI, Request
import requests
import os
import json
from transformers import pipeline

# Initialize FastAPI
app = FastAPI()

# Initialize a text-generation pipeline with a local model
generator = pipeline("text-generation", model="TheBloke/Llama-2-7B-Chat-GGUF", device_map="auto")

# Initialize SURF client functions
def search_web(query, max_results=5):
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": query, "format": "json", "max_results": max_results}
    )
    return response.json()

def read_webpage(url):
    response = requests.get(
        f"http://localhost:8000/read/{url}",
        params={"format": "json"}
    )
    return response.json()

@app.post("/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    
    messages = data.get("messages", [])
    user_message = next((m for m in reversed(messages) if m["role"] == "user"), None)
    
    if not user_message:
        return {"error": "No user message found"}
    
    # Check if the message contains commands for web search or reading
    query = user_message["content"].lower()
    response_content = ""
    
    if "search for:" in query:
        search_query = query.split("search for:")[1].strip()
        search_results = search_web(search_query)
        
        # Format search results
        response_content = f"Here are the search results for '{search_query}':\n\n"
        for i, result in enumerate(search_results["results"], 1):
            response_content += f"{i}. {result['title']}\n   {result['url']}\n   {result['snippet']}\n\n"
    
    elif "read webpage:" in query:
        url = query.split("read webpage:")[1].strip()
        webpage_content = read_webpage(url)
        
        # Format webpage content
        response_content = f"Content from {webpage_content['title']} ({webpage_content['url']}):\n\n"
        response_content += webpage_content['content'][:1000]  # Truncate for brevity
        response_content += "\n\n(Content truncated for brevity)"
    
    else:
        # Regular text generation for other queries
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        generated = generator(prompt, max_length=500, do_sample=True, temperature=0.7)
        response_content = generated[0]["generated_text"].split("assistant:")[-1].strip()
    
    return {
        "id": "chatcmpl-" + os.urandom(12).hex(),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "local-llm",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt),
            "completion_tokens": len(response_content),
            "total_tokens": len(prompt) + len(response_content)
        }
    }
```

## Troubleshooting

### Common Issues and Solutions

1. **Connection Errors**

   If you're experiencing connection errors to the SURF API:
   
   ```
   Error: Connection refused
   ```
   
   **Solution**: Ensure the SURF API is running and accessible at the expected URL. Check if the port is correct and not blocked by a firewall.

2. **Rate Limiting or Timeout Issues**

   If SearXNG requests are timing out:
   
   ```
   Error: Timeout when contacting SearXNG
   ```