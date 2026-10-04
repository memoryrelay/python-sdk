"""LlamaIndex integration for MemoryRelay.

Provides a ChatStore implementation backed by MemoryRelay,
allowing LlamaIndex agents to use persistent conversation memory.

Usage:
    pip install memoryrelay[llamaindex]

    from memoryrelay.integrations.llamaindex import MemoryRelayChatStore

    chat_store = MemoryRelayChatStore(
        api_key="your-api-key",
    )
    chat_store.set_messages("agent-1", [ChatMessage(role="user", content="Hi")])
    messages = chat_store.get_messages("agent-1")
"""

from __future__ import annotations

try:
    from llama_index.core.llms import ChatMessage, MessageRole
    from llama_index.core.storage.chat_store import BaseChatStore
except ImportError:
    raise ImportError(
        "LlamaIndex is required for this integration. "
        "Install it with: pip install memoryrelay[llamaindex]"
    )

from memoryrelay import MemoryCreate, MemoryRelay


class MemoryRelayChatStore(BaseChatStore):
    """LlamaIndex chat store backed by MemoryRelay.

    Maps LlamaIndex's key-based message storage to MemoryRelay's
    agent-scoped memory system. Each `key` maps to an agent_id.

    Args:
        api_key: MemoryRelay API key.
        base_url: API base URL (default: https://api.memoryrelay.net).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.memoryrelay.net",
    ):
        self._client = MemoryRelay(api_key=api_key, base_url=base_url)

    @classmethod
    def class_name(cls) -> str:
        return "MemoryRelayChatStore"

    def set_messages(self, key: str, messages: list[ChatMessage]) -> None:
        """Set messages for a key (agent_id), replacing existing."""
        # Clear existing messages for this key
        self.delete_messages(key)
        # Add new messages
        for msg in messages:
            self.add_message(key, msg)

    def get_messages(self, key: str) -> list[ChatMessage]:
        """Get all messages for a key (agent_id)."""
        memory_list = self._client.memories.list(agent_id=key, limit=1000)

        messages: list[ChatMessage] = []
        for mem in memory_list.memories:
            role_str = (mem.metadata or {}).get("role", "user")
            try:
                role = MessageRole(role_str)
            except ValueError:
                role = MessageRole.USER
            messages.append(ChatMessage(role=role, content=mem.content))

        return messages

    def add_message(self, key: str, message: ChatMessage) -> None:
        """Add a message for a key (agent_id)."""
        self._client.memories.create(
            MemoryCreate(
                agent_id=key,
                content=message.content,
                metadata={
                    "role": message.role.value,
                    "source": "llamaindex",
                },
            )
        )

    def delete_messages(self, key: str) -> list[ChatMessage] | None:
        """Delete all messages for a key (agent_id)."""
        memory_list = self._client.memories.list(agent_id=key, limit=1000)
        deleted: list[ChatMessage] = []
        for mem in memory_list.memories:
            role_str = (mem.metadata or {}).get("role", "user")
            try:
                role = MessageRole(role_str)
            except ValueError:
                role = MessageRole.USER
            deleted.append(ChatMessage(role=role, content=mem.content))
            self._client.memories.delete(mem.id)
        return deleted

    def delete_message(self, key: str, idx: int) -> ChatMessage | None:
        """Delete a specific message by index."""
        memory_list = self._client.memories.list(agent_id=key, limit=1000)
        memories = memory_list.memories
        if idx < 0 or idx >= len(memories):
            return None
        mem = memories[idx]
        role_str = (mem.metadata or {}).get("role", "user")
        try:
            role = MessageRole(role_str)
        except ValueError:
            role = MessageRole.USER
        self._client.memories.delete(mem.id)
        return ChatMessage(role=role, content=mem.content)

    def delete_last_message(self, key: str) -> ChatMessage | None:
        """Delete the last message for a key."""
        memory_list = self._client.memories.list(agent_id=key, limit=1000)
        memories = memory_list.memories
        if not memories:
            return None
        return self.delete_message(key, len(memories) - 1)

    def get_keys(self) -> list[str]:
        """Get all keys (agent IDs).

        Note: This lists all agents for the authenticated user.
        """
        agents = self._client.agents.list()
        return [agent.id for agent in agents.agents]
