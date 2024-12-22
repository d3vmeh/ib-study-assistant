from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import base64
import os

def grade_frq_response(context, question):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            "You are an IB study assistant, tutor, and grader. You are helping score and explain responses to IB questions. Speak to the student directly in a friendly manner."
        ),
        (
            "user",
            """


            The following context includes the question and the markscheme:
            {context}


            Here is the student's response:
            {question}"""
        ),
        ]
        )
    
    print(context)
    chain = (
         {"context": lambda x: context, "question": RunnablePassthrough()}
         | prompt
         | llm
         | StrOutputParser()
    )
    #response_text = model.invoke(prompt)
    try:
        response_text = chain.invoke(question)
    except:
        response_text = "Error generating response. May be an API key issue."
    return response_text


def encode_image_from_file(image_path);
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_chat_response(context, question, image_url = None):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    messages = [
        SystemMessage(content="You are an IB study assistant, tutor, and grader. You are helping score and explain responses to IB questions. Speak to the student directly in a friendly manner."),
    ]

    user_content = {
        "type": "text",
        "text": f"""
        Here are your previous conversations with the student:

        {context}


        Here is the question:
        {question}"""
    }

    if image_url:
        message_content = [
            user_content,
            {
                "type": "image_url",
                "image_url": image_url
            }
        ]
    else:
        message_content = user_content
    
    messages.append(HumanMessage(content=message_content))

    try:
        response = llm.invoke(messages)
        return response.content
    
    except:
        return "Error generating response. May be an API key issue."
    #prompt = ChatPromptTemplate.from_messages(
    #    [
    #    (
    #        "system",
    #        "You are an IB study assistant, tutor, and grader. You are helping score and explain responses to IB questions. Speak to the student directly in a friendly manner."
    #    ),
    #    (
    #        "user",
    #        """
    #        Here are your previous conversations with the student:
    #
    #        {context}
    #
    #
    #        Here is the question:
    #        {question}"""
    #    ),
    #    ]
    #    )
    #
    #print(context)
    #chain = (
    #     {"context": lambda x: context, "question": RunnablePassthrough()}
    #     | prompt
    #     | llm
    #     | StrOutputParser()
    #)
    ##response_text = model.invoke(prompt)
    #try:
    #    response_text = chain.invoke(question)
    #except:
    #    response_text = "Error generating response. May be an API key issue."
    #return response_text