# -*- coding: utf-8 -*-

import os
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks.manager import get_openai_callback
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from extractcontent3 import ExtractContent

def summary(args):
    if args.pdf is not None:
        pages = pdf_to_text(args.pdf)
    elif args.pdf_url is not None:
        file = pdf_download(args.pdf_url)
        pages = pdf_to_text(file)
    elif args.url is not None:
        docs = extract_html(args.url)
        pages = character_split(docs)

    if pages is not None:
        answer = extract(pages)
        return answer

def character_split(words):
    print(words)
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=0
    )

    pages = text_splitter.create_documents([words])
    return pages

def pdf_download(url):
    response = requests.get(url)
    file_path = "/tmp/naobot.pdf"

    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)

    return file_path

def pdf_to_text(file):
    loader = PyPDFLoader(file)
    pages = loader.load_and_split()

    return pages

def extract(pages):
    llm = ChatOpenAI(
        model='gpt-4o-mini',
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    embeddings = OpenAIEmbeddings()

    vectorstore = Chroma.from_documents(
        pages, embedding=embeddings, persist_directory="."
    )

    pdf_qa = ConversationalRetrievalChain.from_llm(
        llm, vectorstore.as_retriever(), return_source_documents=True
    )

    chat_history = []

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break

        with get_openai_callback() as cb:
            result = pdf_qa.invoke(
                {"question": user_input, "chat_history": chat_history}
            )
            print(result['answer'])

    return "Done"

def extract_html(url):
    extractor = ExtractContent()

    opt = {
        "threshold": 80,
    }
    extractor.set_option(opt)

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    header = {"User-Agent": user_agent}

    res = requests.get(url, headers=header)
    html = res.text

    extractor.analyse(html)
    text, title = extractor.as_text()

    return text