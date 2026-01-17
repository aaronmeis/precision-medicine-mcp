"""Chat handler for Claude API with MCP servers.

Handles message formatting, API calls, and response parsing.
"""

import os
from typing import List, Dict, Optional
import anthropic


class ChatHandler:
    """Handle chat interactions with Claude API and MCP servers."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize chat handler.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def send_message(
        self,
        messages: List[Dict[str, str]],
        mcp_servers: List[Dict],
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> anthropic.types.Message:
        """Send message to Claude with MCP servers enabled.

        Args:
            messages: Chat messages history
            mcp_servers: MCP server configurations
            model: Claude model to use
            max_tokens: Maximum response tokens
            temperature: Sampling temperature

        Returns:
            Claude API response message
        """
        # Get tools config for selected servers
        tools = [
            {"type": "mcp_toolset", "mcp_server_name": server["name"]}
            for server in mcp_servers
        ]

        # Build system prompt instructing Claude to use MCP tools
        server_descriptions = []
        for server in mcp_servers:
            server_descriptions.append(f"- {server['name']}: Available for bioinformatics analysis")

        system_prompt = f"""You are a bioinformatics assistant with access to specialized analysis tools via MCP servers.

IMPORTANT: When users ask you to perform analysis, you MUST use the appropriate MCP tool rather than providing theoretical responses.

Available MCP servers:
{chr(10).join(server_descriptions)}

Guidelines:
- When asked to perform pathway enrichment, spatial analysis, or other bioinformatics tasks, USE THE TOOLS
- Call the appropriate MCP tool to get real analysis results
- After receiving tool results, interpret and explain them to the user
- Provide actionable insights based on the actual analysis output
- If you don't have access to a required tool, let the user know

Do not simulate or describe what an analysis would show - actually perform it using the available tools."""

        try:
            response = self.client.beta.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                mcp_servers=mcp_servers,
                tools=tools,
                system=system_prompt,
                betas=["mcp-client-2025-11-20"]
            )
            return response

        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def format_response(self, response: anthropic.types.Message) -> str:
        """Format Claude response for display.

        Args:
            response: Claude API response

        Returns:
            Formatted response text
        """
        if not response.content:
            return "No response from Claude"

        # Extract text from content blocks
        parts = []
        for block in response.content:
            if hasattr(block, 'text'):
                parts.append(block.text)
            elif isinstance(block, dict) and 'text' in block:
                parts.append(block['text'])

        return "\n\n".join(parts) if parts else "Empty response"

    def get_usage_info(self, response: anthropic.types.Message) -> Dict:
        """Extract usage information from response.

        Args:
            response: Claude API response

        Returns:
            Dict with token usage info
        """
        usage = response.usage if hasattr(response, 'usage') else None
        if usage:
            return {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.input_tokens + usage.output_tokens
            }
        return {}
