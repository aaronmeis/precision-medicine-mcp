#!/usr/bin/env python3
"""Test script to verify Jupyter notebook functionality."""

import os
import sys
from dotenv import load_dotenv
import anthropic
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# MCP Server Configuration
MCP_SERVERS = {
    "fgbio": {
        "url": "https://mcp-fgbio-ondu7mwjpa-uc.a.run.app/sse",
        "description": "Genomic reference data and FASTQ validation"
    },
    "spatialtools": {
        "url": "https://mcp-spatialtools-ondu7mwjpa-uc.a.run.app/sse",
        "description": "Spatial transcriptomics analysis tools"
    },
    "multiomics": {
        "url": "https://mcp-multiomics-ondu7mwjpa-uc.a.run.app/sse",
        "description": "Multi-omics data integration"
    }
}

class MCPClient:
    """Helper class for calling MCP servers via Claude API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY not found in environment")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.conversation_history = []
        print("✅ API Key configured")

    def call_servers(
        self,
        prompt: str,
        servers: List[str],
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 4096,
        clear_history: bool = False
    ) -> Dict[str, Any]:
        """Call MCP servers with a prompt."""
        if clear_history:
            self.conversation_history = []

        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # Build MCP server configs
        mcp_servers = [
            {
                "type": "url",
                "url": MCP_SERVERS[server]["url"],
                "name": server
            }
            for server in servers
            if server in MCP_SERVERS
        ]

        # Build tools list
        tools = [
            {"type": "mcp_toolset", "mcp_server_name": server}
            for server in servers
            if server in MCP_SERVERS
        ]

        print(f"\n🔧 Calling {len(servers)} MCP server(s): {', '.join(servers)}")
        print(f"📝 Prompt: {prompt[:80]}...")

        try:
            # Call Claude API with MCP servers
            response = self.client.beta.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=self.conversation_history,
                mcp_servers=mcp_servers,
                tools=tools,
                betas=["mcp-client-2025-11-20"]
            )

            # Extract response text
            response_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    response_text += block.text

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Calculate costs (approximate)
            input_cost = response.usage.input_tokens * 0.003 / 1000
            output_cost = response.usage.output_tokens * 0.015 / 1000
            total_cost = input_cost + output_cost

            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                "estimated_cost_usd": total_cost
            }

            print(f"✅ Response received")
            print(f"📊 Tokens: {usage['input_tokens']} in, {usage['output_tokens']} out")
            print(f"💵 Cost: ${usage['estimated_cost_usd']:.4f}")

            return {
                "response": response_text,
                "usage": usage,
                "model": model,
                "servers_used": servers
            }

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise

def test_api_key():
    """Test 1: Verify API key is configured."""
    print("=" * 60)
    print("TEST 1: API Key Configuration")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ API Key found: {api_key[:20]}...")
        return True
    else:
        print("❌ API Key not found")
        return False

def test_mcp_client():
    """Test 2: Initialize MCP Client."""
    print("\n" + "=" * 60)
    print("TEST 2: MCPClient Initialization")
    print("=" * 60)

    try:
        client = MCPClient()
        print("✅ MCPClient initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return None

def test_simple_query(client):
    """Test 3: Simple MCP query."""
    print("\n" + "=" * 60)
    print("TEST 3: Simple MCP Query (List Available Tools)")
    print("=" * 60)

    try:
        result = client.call_servers(
            prompt="List all available tools from the spatialtools server.",
            servers=["spatialtools"],
            max_tokens=2048
        )

        print("\n📝 Response:")
        print("-" * 60)
        print(result["response"][:500])
        if len(result["response"]) > 500:
            print(f"... (truncated, full length: {len(result['response'])} chars)")
        print("-" * 60)

        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🧪 TESTING JUPYTER NOTEBOOK MCP CLIENT")
    print("=" * 60)

    # Test 1: API Key
    if not test_api_key():
        print("\n❌ FAILED: API key not configured")
        sys.exit(1)

    # Test 2: Client initialization
    client = test_mcp_client()
    if not client:
        print("\n❌ FAILED: Could not initialize client")
        sys.exit(1)

    # Test 3: Simple query
    if not test_simple_query(client):
        print("\n❌ FAILED: Query failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✨ The Jupyter notebook is ready to use!")
    print("   Run: jupyter notebook mcp_client.ipynb")
    print("")

if __name__ == "__main__":
    main()
