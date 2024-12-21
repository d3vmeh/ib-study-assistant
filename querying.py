from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain

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



def get_chat_response(context, question):
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
            Here are your previous conversations with the student:

            {context}


            Here is the question:
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