# SURF API: Use Cases and Applications

SURF API bridges the gap between LLMs and the web, enabling a new class of applications. This document outlines key use cases, benefits, and real-world applications.

## Key Benefits

### For Developers

1. **Simplified Web Integration**
   - Eliminate complex web scraping code
   - Standardized content processing across different sites
   - No need to handle different HTML structures manually

2. **Enhanced LLM Performance**
   - Provide clean, structured data to your LLMs
   - Reduce token usage by removing unnecessary content
   - Better formatting preserves semantic structure

3. **Privacy and Control**
   - Self-hosted solution keeps user queries private
   - Control over what content is accessed and how
   - No dependency on third-party web access APIs

4. **Flexibility**
   - Multiple output formats (JSON, markdown)
   - Configurable content processing options
   - Easily integrates with any LLM framework

### For End Users

1. **Up-to-date Information**
   - Access to current information beyond the LLM's training data
   - Real-time web search capabilities
   - Access to the latest articles, documentation, and content

2. **Better Answers**
   - Responses based on factual, current web content
   - Citations and sources for information
   - Reduced hallucinations from LLMs

3. **Tool-like Capabilities**
   - Web research assistant capabilities
   - Information gathering from multiple sources
   - Content summarization and analysis

## Use Cases

### 1. Research Assistant Applications

**Scenario**: A user needs to research a complex topic with many facets.

**Implementation**:
1. User submits a research query
2. Application uses SURF to search for relevant sources
3. For each promising source, the content is fetched and processed
4. The LLM analyzes, synthesizes, and summarizes the information
5. The user receives a comprehensive research report with citations

**Benefits**:
- Access to up-to-date information
- Multiple source validation
- Proper citations and attribution
- Structured, comprehensive results

### 2. Knowledge Base Enhancement

**Scenario**: An enterprise has internal documentation but needs to supplement it with external information.

**Implementation**:
1. When user queries the knowledge base
2. System first searches internal sources
3. If information is insufficient, SURF searches the web
4. External information is blended with internal knowledge
5. Response clearly differentiates between internal and external knowledge

**Benefits**:
- Extends internal knowledge bases
- Keeps information current
- Clear source attribution
- Consistent formatting of internal and external information

### 3. Technical Documentation Assistant

**Scenario**: Developers need help understanding and implementing technical solutions.

**Implementation**:
1. Developer asks a coding or technical question
2. System searches for relevant documentation and tutorials
3. SURF fetches and processes the content, preserving code blocks and tables
4. LLM synthesizes a solution based on multiple documentation sources
5. Developer receives contextual, accurate guidance

**Benefits**:
- Code examples are properly formatted
- Technical tables are preserved
- Solutions based on current documentation
- Multiple sources for better answers

### 4. News Analysis and Summarization

**Scenario**: Users want to stay informed about a topic with analysis of recent developments.

**Implementation**:
1. User requests news on a specific topic
2. SURF searches for recent news articles
3. Content from multiple sources is fetched and processed
4. LLM analyzes, compares, and summarizes the perspectives
5. User receives a balanced overview with links to original sources

**Benefits**:
- Multiple source perspective
- Up-to-date information
- Reduced bias through multi-source analysis
- Original sources available for deeper reading

### 5. Fact-Checking and Verification

**Scenario**: Users want to verify claims or statements.

**Implementation**:
1. User submits a claim to verify
2. SURF searches for relevant information
3. Multiple sources are fetched and processed
4. LLM analyzes the consistency and credibility of information
5. User receives a verification result with supporting evidence

**Benefits**:
- Multiple source verification
- Access to current information
- Clear presentation of evidence
- Reduced LLM hallucination

## Real-World Applications

### Educational Tools

**Example**: A study assistant that helps students research topics, understand concepts, and find supplementary resources.

**How SURF Helps**:
- Fetches and processes educational content from various sources
- Preserves mathematical formulas and scientific notation
- Structures information in a learning-friendly format
- Provides current, accurate information for projects and assignments

### Business Intelligence

**Example**: A market research tool that gathers and analyzes information about competitors, trends, and industry developments.

**How SURF Helps**:
- Searches for current market information
- Processes business news, reports, and analyses
- Extracts structured data from different sources
- Enables continuous monitoring of market changes

### Healthcare Information Systems

**Example**: A clinical information assistant that helps healthcare professionals stay updated on research and treatment guidelines.

**How SURF Helps**:
- Searches medical journals and trusted health sources
- Preserves critical data tables and research findings
- Extracts structured information from clinical guidelines
- Provides current information beyond the LLM's training cutoff

### Legal Research

**Example**: A legal research assistant that helps lawyers find relevant cases, statutes, and legal analyses.

**How SURF Helps**:
- Searches legal databases and resources
- Preserves citation formats and legal terminology
- Structures complex legal documents for easier analysis
- Provides up-to-date legal information and precedents

### Content Creation Support

**Example**: A content creation assistant that helps writers research topics, find statistics, and verify information.

**How SURF Helps**:
- Gathers information from multiple sources
- Extracts statistics, quotes, and key facts
- Provides proper attribution for content
- Ensures factual accuracy in created content

## Integration Strategies

### 1. Tool-Based Approach

Implement SURF as a tool that your LLM can call when it needs information:

```python
def answer_with_web_info(question):
    # First try to answer with local knowledge
    initial_answer = llm.generate(f"Answer this question: {question}")
    
    # Check if confidence is low or needs verification
    if "I don't know" in initial_answer or "I'm not sure" in initial_answer:
        # Search for information
        search_results = requests.get(
            "http://localhost:8000/search",
            params={"q": question, "format": "json", "max_results": 3}
        ).json()
        
        # Get content from top results
        sources = []
        for result in search_results["results"][:2]:
            content = requests.get(
                f"http://localhost:8000/read/{result['url']}",
                params={"format": "json"}
            ).json()
            sources.append(content)
        
        # Create prompt with sources
        source_text = "\n\n".join([
            f"SOURCE: {source['title']}\n{source['content']}"
            for source in sources
        ])
        
        prompt = f"""
        Question: {question}
        
        Please answer the question based on these sources:
        
        {source_text}
        
        Answer:
        """
        
        # Generate answer with sources
        return llm.generate(prompt)
    
    return initial_answer
```

### 2. RAG Architecture

Implement a Retrieval-Augmented Generation system using SURF as the retriever:

```python
class SURFRetriever:
    def __init__(self, search_results_count=3, content_results_count=2):
        self.search_results_count = search_results_count
        self.content_results_count = content_results_count
        
    async def retrieve(self, query):
        # Search the web
        search_results = requests.get(
            "http://localhost:8000/search",
            params={"q": query, "format": "json", "max_results": self.search_results_count}
        ).json()
        
        # Get content from top results
        documents = []
        for result in search_results["results"][:self.content_results_count]:
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

# Usage in RAG system
retriever = SURFRetriever()
documents = await retriever.retrieve("latest developments in quantum computing")

# Generate with retrieved context
context = "\n\n".join([f"SOURCE: {doc['title']} ({doc['url']})\n{doc['content']}" for doc in documents])
response = llm.generate(f"Context:\n{context}\n\nBased on the above information, what are the latest developments in quantum computing?")
```

### 3. Hybrid Approach

Combine local knowledge with web information:

```python
def hybrid_answer(question):
    # 1. Try to answer with local knowledge
    local_answer = llm.generate(
        f"Question: {question}\nAnswer using only your built-in knowledge. If you're unsure, say 'NEED_WEB_SEARCH'."
    )
    
    # 2. If local knowledge is insufficient, use web search
    if "NEED_WEB_SEARCH" in local_answer:
        # Use SURF to get web information
        web_info = get_web_information(question)
        
        # Generate answer with web info
        web_answer = llm.generate(
            f"Question: {question}\nInformation from the web: {web_info}\nAnswer based on this information:"
        )
        
        # Return with attribution
        return f"{web_answer}\n\nThis answer is based on current web information."
    
    return local_answer
```

### 4. Model Context Protocol (MCP) Integration

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that enables AI assistants to interact with external data sources and tools in a standardized way. SURF makes implementing MCP servers remarkably easy, allowing your AI applications to access web information through a standardized interface.

**Example**: Creating a SURF-based MCP server for web search and content retrieval:

```python
from mcp import MCPServer, ServerSchema, RequestContext
import requests

# Define SURF MCP server with minimal boilerplate
schema = ServerSchema(
    name="surf-web-access",
    description="Web search and content reading via SURF",
    capabilities=[
        {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "read_webpage",
            "description": "Read content from a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to read"}
                },
                "required": ["url"]
            }
        }
    ]
)

# Simple handler that directly leverages SURF API
async def search_web(context: RequestContext, params: dict):
    response = requests.get(
        "http://localhost:8000/search",
        params={"q": params["query"], "format": "json"}
    )
    return response.json()

async def read_webpage(context: RequestContext, params: dict):
    response = requests.get(
        f"http://localhost:8000/read/{params['url']}",
        params={"format": "json"}
    )
    return response.json()

# Create and start MCP server
server = MCPServer(schema=schema)
server.register_capability("search_web", search_web)
server.register_capability("read_webpage", read_webpage)
server.start()
```

**Benefits of SURF-based MCP Servers**:

1. **Simplified Implementation**: SURF handles the complex web processing, allowing your MCP server to be clean and focused
2. **Standardized Integration**: Any MCP-compatible AI assistant (like Claude) can use your server
3. **Enhanced AI Capabilities**: Give AI models access to up-to-date web information and content
4. **Rapid Development**: Create powerful MCPs with minimal code by leveraging SURF's robust web processing

**Real-world Applications**:

- **Knowledge Management Systems**: Create an MCP that searches both internal documentation and the web
- **Research Assistants**: Enable AI to gather information from multiple sources through a unified MCP interface
- **Customer Support**: Let AI representatives look up product information, policies, and external references
- **Content Creation**: Provide AI with the ability to research topics and gather accurate information

By leveraging SURF to create MCP servers, developers can quickly enable AI systems to interact with the web in a standardized, secure way, without needing to implement complex web crawling or content processing logic.

## Best Practices

1. **Clear Source Attribution**
   - Always provide sources for information retrieved from the web
   - Include URLs and titles when presenting information to users

2. **Multiple Source Verification**
   - Use multiple sources to verify information
   - Compare information across different sources for accuracy

3. **Content Freshness Awareness**
   - Check publication dates when available
   - Prioritize recent sources for time-sensitive topics

4. **Error Handling**
   - Implement robust error handling for network issues
   - Have fallback strategies when web search fails

5. **User Transparency**
   - Clearly indicate when information comes from the web
   - Distinguish between the LLM's knowledge and web-retrieved information 