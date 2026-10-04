"""LangChain integration for MemoryRelay.

Provides a ChatMessageHistory implementation backed by MemoryRelay,
allowing LangChain chains and agents to use persistent memory.

Usage:
    pip install memoryrelay[langchain]

    from memoryrelay.integrations.langchain import MemoryRelayChatMessageHistory

    history = MemoryRelayChatMessageHistory(
        api_key="your-api-key",
        agent_id="your-agent-id",
    )
    history.add_user_message("Hello!")
    history.add_ai_message("Hi there!")
    messages = history.messages
"""

from __future__ import annotations

try:
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
except ImportError:
    raise ImportError(
        "LangChain is required for this integration. "
        "Install it with: pip install memoryrelay[langchain]"
    )

from memoryrelay import MemoryCreate, MemoryRelay, MemorySearchRequest


class MemoryRelayChatMessageHistory(BaseChatMessageHistory):
    """LangChain chat message history backed by MemoryRelay.

    Stores each message as a separate memory with role metadata.
    Retrieves messages by querying the agent's memory store.

    Args:
        api_key: MemoryRelay API key.
        agent_id: Agent ID to scope memories to.
        base_url: API base URL (default: https://api.memoryrelay.net).
        session_id: Optional session ID for filtering conversations.
        limit: Max messages to retrieve (default: 100).
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: str = "https://api.memoryrelay.net",
        session_id: str | None = None,
        limit: int = 100,
    ):
        self._client = MemoryRelay(api_key=api_key, base_url=base_url)
        self._agent_id = agent_id
        self._session_id = session_id
        self._limit = limit

    @property
    def messages(self) -> list[BaseMessage]:
        """Retrieve all messages from MemoryRelay."""
        memory_list = self._client.memories.list(
            agent_id=self._agent_id,
            limit=self._limit,
        )

        messages: list[BaseMessage] = []
        for mem in memory_list.memories:
            role = (mem.metadata or {}).get("role", "human")
            # Filter by session_id if specified
            if self._session_id:
                mem_session = (mem.metadata or {}).get("session_id")
                if mem_session != self._session_id:
                    continue
            if role == "ai":
                messages.append(AIMessage(content=mem.content))
            else:
                messages.append(HumanMessage(content=mem.content))

        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the MemoryRelay store."""
        role = "ai" if isinstance(message, AIMessage) else "human"
        metadata = {"role": role, "source": "langchain"}
        if self._session_id:
            metadata["session_id"] = self._session_id

        self._client.memories.create(
            MemoryCreate(
                agent_id=self._agent_id,
                content=message.content,
                metadata=metadata,
            )
        )

    def clear(self) -> None:
        """Clear all messages for this agent (deletes memories)."""
        memory_list = self._client.memories.list(
            agent_id=self._agent_id,
            limit=1000,
        )
        for mem in memory_list.memories:
            if self._session_id:
                mem_session = (mem.metadata or {}).get("session_id")
                if mem_session != self._session_id:
                    continue
            self._client.memories.delete(mem.id)

    def search(self, query: str, limit: int = 5) -> list[BaseMessage]:
        """Semantic search across message history.

        This is a MemoryRelay-specific extension beyond the base LangChain
        interface, enabling RAG-style retrieval from conversation history.

        Args:
            query: Natural language search query.
            limit: Max results to return.

        Returns:
            List of matching messages ranked by relevance.
        """
        results = self._client.memories.search(
            MemorySearchRequest(
                query=query,
                agent_id=self._agent_id,
                limit=limit,
            )
        )

        messages: list[BaseMessage] = []
        for result in results.results:
            role = (result.metadata or {}).get("role", "human")
            if role == "ai":
                messages.append(AIMessage(content=result.content))
            else:
                messages.append(HumanMessage(content=result.content))

        return messages
