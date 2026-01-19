"""
Streamlit components for displaying orchestration traces.

Provides multiple visualization options:
- Simple text log
- Styled expandable cards
- Timeline visualization
- Mermaid sequence diagram
"""

import streamlit as st
from typing import List, Optional
import json
from .trace_utils import (
    OrchestrationTrace,
    ToolCall,
    get_server_info
)


def render_trace_summary(trace: OrchestrationTrace):
    """Render a one-line summary of the trace."""
    servers = trace.servers_used
    server_icons = " → ".join(
        get_server_info(s)['icon'] for s in servers
    )

    st.caption(
        f"{server_icons} | "
        f"{trace.call_count} calls | "
        f"{trace.total_duration_ms:.0f}ms | "
        f"~${trace.estimated_cost_usd:.4f}"
    )


def render_trace_log(trace: OrchestrationTrace):
    """
    Render a simple text-based trace log.

    This is the most compact view, suitable for quick inspection.
    """
    with st.expander(
        f"🔍 Orchestration Trace ({trace.call_count} server calls)",
        expanded=False
    ):
        # Summary metrics
        cols = st.columns(4)
        cols[0].metric("Servers", len(trace.servers_used))
        cols[1].metric("Calls", trace.call_count)
        cols[2].metric("Duration", f"{trace.total_duration_ms:.0f}ms")
        cols[3].metric("Cost", f"${trace.estimated_cost_usd:.4f}")

        st.divider()

        # Step-by-step log
        for tc in trace.tool_calls:
            server_info = get_server_info(tc.server_name)

            st.markdown(f"""
**Step {tc.step_number}: {server_info['icon']} {server_info['display_name']}**

- **Tool:** `{tc.tool_name}`
- **Input:** `{_format_input(tc.input_params)}`
{f"- **Result:** {tc.result_summary}" if tc.result_summary else ""}
            """)
            st.divider()


def render_trace_cards(trace: OrchestrationTrace):
    """
    Render the trace as styled cards.

    More visual than the log view, shows server icons prominently.
    """
    with st.expander(
        f"🔍 Orchestration Trace ({trace.call_count} server calls)",
        expanded=False
    ):
        # Summary row
        render_trace_summary(trace)
        st.divider()

        # Cards in columns (2 per row)
        for i in range(0, len(trace.tool_calls), 2):
            cols = st.columns(2)

            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(trace.tool_calls):
                    tc = trace.tool_calls[idx]
                    server_info = get_server_info(tc.server_name)

                    with col:
                        st.markdown(f"""
<div style="
    background-color: {server_info['color']};
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
">
    <h4 style="margin: 0;">{server_info['icon']} Step {tc.step_number}</h4>
    <p style="margin: 0.5rem 0 0 0; font-weight: bold;">{server_info['display_name']}</p>
    <p style="margin: 0.25rem 0; font-size: 0.9em;"><code>{tc.tool_name}</code></p>
    <p style="margin: 0; font-size: 0.8em; color: #666;">{server_info['description']}</p>
</div>
                        """, unsafe_allow_html=True)


def render_trace_timeline(trace: OrchestrationTrace):
    """
    Render a horizontal timeline visualization.

    Best for showing the flow of the orchestration.
    """
    with st.expander(
        f"🔍 Orchestration Trace ({trace.call_count} server calls)",
        expanded=False
    ):
        # Build timeline HTML
        timeline_items = []
        for tc in trace.tool_calls:
            server_info = get_server_info(tc.server_name)
            timeline_items.append(f"""
<div style="
    display: inline-block;
    text-align: center;
    padding: 0.5rem 1rem;
    margin: 0 0.25rem;
    background-color: {server_info['color']};
    border-radius: 0.5rem;
    min-width: 100px;
">
    <div style="font-size: 1.5rem;">{server_info['icon']}</div>
    <div style="font-size: 0.8rem; font-weight: bold;">{server_info['display_name']}</div>
    <div style="font-size: 0.7rem; color: #666;">{tc.tool_name}</div>
</div>
            """)

        # Add arrows between items
        timeline_html = " → ".join(timeline_items)

        st.markdown(f"""
<div style="
    display: flex;
    align-items: center;
    justify-content: flex-start;
    overflow-x: auto;
    padding: 1rem 0;
">
    {timeline_html}
</div>
        """, unsafe_allow_html=True)

        # Summary below
        st.caption(
            f"Total: {trace.total_duration_ms:.0f}ms | "
            f"{trace.total_tokens:,} tokens | "
            f"~${trace.estimated_cost_usd:.4f}"
        )


def _generate_mermaid_code(trace: OrchestrationTrace) -> str:
    """Generate Mermaid sequence diagram code for a trace."""
    mermaid_lines = [
        "sequenceDiagram",
        "    participant User",
        "    participant Claude"
    ]

    # Add unique servers as participants
    seen_servers = set()
    for tc in trace.tool_calls:
        if tc.server_name not in seen_servers:
            server_info = get_server_info(tc.server_name)
            alias = tc.server_name.replace('-', '_')
            mermaid_lines.append(
                f"    participant {alias} as {server_info['icon']} {server_info['display_name']}"
            )
            seen_servers.add(tc.server_name)

    # Add the initial query
    query_short = trace.query[:50] + "..." if len(trace.query) > 50 else trace.query
    mermaid_lines.append(f"    User->>Claude: {query_short}")

    # Add tool calls
    for tc in trace.tool_calls:
        alias = tc.server_name.replace('-', '_')
        mermaid_lines.append(f"    Claude->>+{alias}: {tc.tool_name}()")
        if tc.result_summary:
            result_short = tc.result_summary[:30] + "..." if len(tc.result_summary) > 30 else tc.result_summary
            mermaid_lines.append(f"    {alias}-->>-Claude: {result_short}")
        else:
            mermaid_lines.append(f"    {alias}-->>-Claude: result")

    # Add final response
    mermaid_lines.append("    Claude->>User: Analysis complete")

    return "\n".join(mermaid_lines)


def render_trace_mermaid(trace: OrchestrationTrace):
    """
    Render a Mermaid sequence diagram.

    Best for documentation and sharing. Can be copied and used elsewhere.
    """
    with st.expander(
        f"🔍 Orchestration Trace ({trace.call_count} server calls)",
        expanded=False
    ):
        mermaid_code = _generate_mermaid_code(trace)

        # Display the diagram
        st.markdown(f"""
```mermaid
{mermaid_code}
```
        """)

        # Also show copyable code
        with st.expander("📋 Copy Mermaid Code"):
            st.code(mermaid_code, language="mermaid")


def render_trace(
    trace: OrchestrationTrace,
    style: str = "log"
):
    """
    Render an orchestration trace in the specified style.

    Args:
        trace: The OrchestrationTrace to render
        style: One of "log", "cards", "timeline", "mermaid"
    """
    if not trace.tool_calls:
        st.caption("ℹ️ No MCP server calls in this response")
        return

    if style == "log":
        render_trace_log(trace)
    elif style == "cards":
        render_trace_cards(trace)
    elif style == "timeline":
        render_trace_timeline(trace)
    elif style == "mermaid":
        render_trace_mermaid(trace)
    else:
        render_trace_log(trace)  # Default


def render_trace_export(trace: OrchestrationTrace, trace_id: int = 0):
    """Render export options for the trace.

    Args:
        trace: OrchestrationTrace object
        trace_id: Unique identifier for this trace (e.g., message index)
    """
    col1, col2 = st.columns(2)

    with col1:
        # Export as JSON
        trace_json = json.dumps({
            "query": trace.query,
            "tool_calls": [
                {
                    "step": tc.step_number,
                    "server": tc.server_name,
                    "tool": tc.tool_name,
                    "input": tc.input_params,
                    "result": tc.result_summary
                }
                for tc in trace.tool_calls
            ],
            "metrics": {
                "duration_ms": trace.total_duration_ms,
                "tokens": trace.total_tokens,
                "cost_usd": trace.estimated_cost_usd
            }
        }, indent=2)

        st.download_button(
            "📥 Download JSON",
            data=trace_json,
            file_name="orchestration_trace.json",
            mime="application/json",
            key=f"download_json_{trace_id}"
        )

    with col2:
        # Copy Mermaid diagram
        mermaid_code = _generate_mermaid_code(trace)
        st.download_button(
            "📥 Download Mermaid",
            data=mermaid_code,
            file_name="orchestration_diagram.mmd",
            mime="text/plain",
            key=f"download_mermaid_{trace_id}"
        )


def _format_input(params: dict) -> str:
    """Format input parameters for display."""
    if not params:
        return "{}"

    # Truncate long values
    formatted = {}
    for k, v in params.items():
        if isinstance(v, str) and len(v) > 50:
            formatted[k] = v[:50] + "..."
        else:
            formatted[k] = v

    return str(formatted)
