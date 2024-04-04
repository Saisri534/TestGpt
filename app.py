import chainlit as cl
import os
from langchain import HuggingFaceHub, PromptTemplate, LLMChain
from components.retriver import Retriever
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory

from chainlit.types import ThreadDict

load_dotenv()
huggingfacehub_api_token = os.environ['HUGGINGFACEHUB_API_TOKEN']
repo_id = "HuggingFaceH4/zephyr-7b-alpha"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token,
                     repo_id=repo_id,
                     model_kwargs={"temperature":0.6, "max_new_tokens":200})

template = """
You are an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.

Context: {context}
Question: {question}
"""
retriever = Retriever.get_retriever()

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Here you would typically query your database or some other service to verify the credentials
    # For demonstration purposes, I'm using hardcoded credentials
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_resume
async def on_chat_resume(thread: cl.ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])
 
    cl.user_session.set("memory", memory)



@cl.on_chat_start
async def main():
    # Store the initial prompt in the user session
    cl.user_session.set("initial_prompt", template)
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(
        content=f"starting chat with {user.identifier} using the {chat_profile} chat profile"
    ).send()


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="GPT-3.5",
            markdown_description="The underlying LLM model is **GPT-3.5**.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GPT-4",
            markdown_description="The underlying LLM model is **GPT-4**.",
            icon="https://picsum.photos/250",
        ),
    ]
 
@cl.on_message
async def main(message):
    memory = cl.user_session.get("memory")
    # Extract the message content if it's a Message object
    if isinstance(message, cl.message.Message):
        message_content = message.content
    else:
        message_content = message
 
    # Check if the message is of type str (string)
    if isinstance(message_content, str):
        # Retrieve the initial prompt from the user session
        initial_prompt = cl.user_session.get("initial_prompt")
       
        # Perform similarity search to retrieve relevant context from the database
        context = retriever.get_relevant_documents(message_content)
        print(context)
       
        input_text = ' '.join([doc.page_content.strip() for doc in context])
        print(input_text)

        # Instantiate the chain for that user session
        prompt_inputs = {"context": input_text, "question": message_content}
        prompt = PromptTemplate(template=initial_prompt, input_variables=["context", "question"])
        llm_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
 
        # Call the chain synchronously with the input dictionary
        response = llm_chain.invoke(input=prompt_inputs, callbacks=[cl.LangchainCallbackHandler()])
        print(response)
 
        # After extracting the LLM answer text from the dictionary
        llm_answer = response["text"]

        # Retrieve metadata from the context
        metadata = {doc.metadata['source'] for doc in context}
        metadata_str = "\n ".join(metadata)

        # Combine the metadata and answer text
        full_answer = f"{llm_answer}\nSources:\n{metadata_str}"

        # Split the text by a separator to separate the context from the answer
        context_separator = "Question:"
        llm_answer_parts = full_answer.split(context_separator)

        # Extract the answer part (assuming it's the second part after splitting)
        if len(llm_answer_parts) > 1:
            answer_text = llm_answer_parts[1].split("\n", 1)[1].strip()  # Split by newline and select the second part
        else:
            answer_text = llm_answer

        # Extract sources from metadata
        sources = metadata_str

        # Send the LLM answer along with sources
        await cl.Message(content=answer_text, elements=[cl.Text(content=sources, name="sources")]).send()
        memory.chat_memory.add_user_message(message_content)
        memory.chat_memory.add_ai_message(answer_text)

    else:
        # If the message is not a string, log an error or handle it appropriately
        print("Received message is not a string:", message_content)
 