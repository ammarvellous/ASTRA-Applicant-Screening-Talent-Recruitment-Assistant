import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI  # for Gemini

load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    api_key=os.getenv("GOOGLE_API_KEY"),
)

# Memory to track chat history
memory = ConversationBufferMemory(return_messages=True)

# Prompt with memory placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI interviewer for ASTRA. Be polite, structured, and context-aware."),
    MessagesPlaceholder(variable_name="history"),   # chat history gets injected here
    ("human", "{input}")                            # new user message
])

# Runnable sequence: prompt + llm
chat_chain = prompt | llm

def ask_llm(user_message: str):
    """Send message to LLM with memory and return reply"""
    history = memory.load_memory_variables({})["history"]

    response = chat_chain.invoke({
        "history": history,
        "input": user_message
    })

    # Save new interaction
    memory.save_context({"input": user_message}, {"output": response.content})

    return response.content
