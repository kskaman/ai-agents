"""Base brain class."""

import requests
import time
import json

from ..tools import Thought, ToolCall


class Brain:
    """Base class for LLM providers."""
    context_limit = 200_000  # 200k tokens
    last_input_tokens = 0  # Updated after each think() call
    streams_output = False

    def think(self, conversation: list[dict]) -> Thought:
        """Process conversation, return Thought."""
        raise NotImplementedError()
    

    def _stream_response(self, url, headers, payload, max_retries=10):
        """Stream an API response, printing tokens as they arrive."""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                   url, headers=headers, json=payload, stream=True,
                    timeout=120)

            except requests.exceptions.RequestException as e:
                wait_time = 2 ** attempt
                print(f"Network error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                retry_after = response.headers.get("retry-after")
                try:
                    wait_time = int(retry_after) if retry_after else 2 ** attempt
                except ValueError:
                    wait_time = 2 ** attempt
                print(f"Error {response.status_code}. Retrying in {wait_time}s...")

                time.sleep(wait_time)
                continue

            if response.status_code >= 400:
                try:
                    error_msg = response.json()["error"]["message"]
                except (KeyError, ValueError):
                    error_msg = response.text
                raise Exception(f"API error ({response.status_code}): {error_msg}")

            break
        else:
            raise Exception(f"Request failed after {max_retries} retries")

        # Track blocks and their content
        blocks = {}  # Per-block state by index
        block_parts = {}  # Per-block text accumulator
        tool_calls = []
        current_index = None
        input_tokens = 0
        in_thinking = False

        for line in response.iter_lines():
            if not line:
                continue
            
            # Decode and strip "data: " prefix
            line = line.decode('utf-8')
            if not line.startswith('data: '):
                continue
                
            data_str = line[6:]
            if data_str.strip() == '[DONE]':
                break
                
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            event_type = data.get("type")

            if event_type == "message_start":
                # Extract input tokens from usage
                usage = data.get("message", {}).get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                
            elif event_type == "error":
                error_data = data.get('error', {})
                raise Exception(f"Stream error: {error_data.get('message', data)}")
                
            elif event_type == "content_block_start":
                block = data.get("content_block", {})
                current_index = data.get("index", 0)
                block_type = block.get("type")
                
                blocks[current_index] = {"type": block_type}
                block_parts[current_index] = []
                
                if block_type == "thinking":
                    in_thinking = True
                    print("\n[thinking] ", end="", flush=True)
                elif block_type == "text":
                    in_thinking = False
                elif block_type == "tool_use":
                    blocks[current_index]["id"] = block.get("id")
                    blocks[current_index]["name"] = block.get("name")
                    
            elif event_type == "content_block_delta":
                delta = data.get("delta", {})
                delta_type = delta.get("type")
                current_index = data.get("index", 0)
                
                if delta_type == "thinking_delta":
                    text = delta.get("thinking", "")
                    block_parts[current_index].append(text)
                    print(text, end="", flush=True)

                elif delta_type == "signature_delta":
                    signature = delta.get("signature", "")
                    blocks[current_index]["signature"] = (
                        blocks[current_index].get("signature", "") + signature
                    )
                    
                elif delta_type == "text_delta":
                    text = delta.get("text", "")
                    block_parts[current_index].append(text)
                    if not in_thinking:
                        print(text, end="", flush=True)
                        
                elif delta_type == "input_json_delta":
                    partial_json = delta.get("partial_json", "")
                    block_parts[current_index].append(partial_json)
                    
            elif event_type == "content_block_stop":
                current_index = data.get("index", 0)
                
                # Finalize block content
                if current_index in block_parts:
                    full_content = "".join(block_parts[current_index])
                    block = blocks[current_index]
                    
                    if block["type"] == "thinking":
                        block["thinking"] = full_content
                        print("\n", end="", flush=True)  # End thinking output
                    elif block["type"] == "text":
                        block["text"] = full_content
                    elif block["type"] == "tool_use":
                        # Parse accumulated JSON
                        try:
                            block["input"] = json.loads(full_content)
                        except json.JSONDecodeError:
                            block["input"] = {}
                            
            elif event_type == "message_delta":
                # Can extract stop_reason if needed
                pass
                
            elif event_type == "message_stop":
                # Stream complete
                break

        print()  # Final newline
        
        # Update input token count
        self.last_input_tokens = input_tokens

        # Build raw_content and extract information
        raw_content = []
        full_text = ""
        full_thinking = None
        
        for idx in sorted(blocks.keys()):
            block = blocks[idx]
            
            if block["type"] == "thinking":
                thinking_block = {
                    "type": "thinking",
                    "thinking": block.get("thinking", "")
                }
                if block.get("signature"):
                    thinking_block["signature"] = block["signature"]
                raw_content.append(thinking_block)
                full_thinking = block.get("thinking", "")
                
            elif block["type"] == "text":
                text = block.get("text", "")
                raw_content.append({
                    "type": "text",
                    "text": text
                })
                full_text += text
                
            elif block["type"] == "tool_use":
                tool_data = {
                    "type": "tool_use",
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "input": block.get("input", {})
                }
                raw_content.append(tool_data)
                
                tool_calls.append(ToolCall(
                    id=block.get("id"),
                    tool_name=block.get("name"),
                    args=block.get("input", {})
                ))

        return Thought(
            text=full_text.strip(),
            tool_calls=tool_calls,
            raw_content=raw_content,
            thinking=full_thinking
        )

    def _parse_response(self, content: list[dict]) -> Thought:
            """Convert Claude's response into a Thought object."""
            text_parts = []
            tool_calls = []
            thinking = None
            filtered_content = []
    
            for block in content:
                if block["type"] == "thinking":
                    thinking = block["thinking"]
                    filtered_content.append(block)
                elif block["type"] == "text":
                    text_parts.append(block["text"])
                    filtered_content.append(block)
                elif block["type"] == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block["id"],
                        tool_name=block["name"],
                        args=block["input"]
                    ))
                    filtered_content.append(block)
    
            return Thought(
                text="\n".join(text_parts) if text_parts else None,
                tool_calls=tool_calls,
                raw_content=filtered_content,  # Only text and tool_use blocks
                thinking=thinking
            )
