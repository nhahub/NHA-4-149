from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import hub

from config.settings import (
    GROK_API_KEY, GROK_BASE_URL, GROK_MODEL,
    LLM_TEMPERATURE, LLM_TIMEOUT, LLM_MAX_RETRIES,
    AGENT_MAX_ITERATIONS, AGENT_VERBOSE,
)
from tools import ALL_TOOLS


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=GROK_API_KEY,
        base_url=GROK_BASE_URL,
        model=GROK_MODEL,
        temperature=LLM_TEMPERATURE,
        request_timeout=LLM_TIMEOUT,
        max_retries=LLM_MAX_RETRIES,
    )


def build_agent_executor() -> AgentExecutor:
    """
    ينشئ AgentExecutor جديد بـ ConversationBufferMemory منفصلة.
    يُستدعى مرة واحدة لكل session جديدة.
    """
    llm    = _build_llm()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    prompt = hub.pull("hwchase17/react-chat")   # يدعم chat_history
    agent  = create_react_agent(llm, ALL_TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=AGENT_VERBOSE,
        max_iterations=AGENT_MAX_ITERATIONS,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )
