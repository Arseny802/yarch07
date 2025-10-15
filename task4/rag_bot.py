#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import logging
from enum import Enum, auto

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM


class RAGBot:
    DB_DIR_POSTFIX = "../task3/faiss_db/"

    class Prompts(Enum):
        BASE = "base"
        FEW_SHOT = "few-shot"
        COT = "cot"

    FILE_BASE_PROMPT = "base_prompt.txt"
    FILE_FEW_SHOT_PROMPT = "few_shot_prompt.txt"
    FILE_COT_PROMPT = "cot_prompt.txt"

    DEFAULT_MAX_DOCUMENTS = 42

    def __init__(
        self,
        setup_dir: str = "",
        rag_max_results=DEFAULT_MAX_DOCUMENTS,
        temperature=0.1,
        verbose=False,
    ):
        self.current_dir = setup_dir or os.path.dirname(os.path.abspath(__file__))
        self.faiss_db_dir = os.path.join(self.current_dir, self.DB_DIR_POSTFIX)
        self.rag_max_results = rag_max_results

        self.vector_db = self._load_db()
        self.ollama = self._connect_ollama(temperature)
        self.prompts = self._create_prompts()
        self._logger = self._setup_logger(verbose)

    def search_documents(self, query: str) -> list[Document]:
        try:
            results = self.vector_db.similarity_search(query, k=self.rag_max_results)
            self._logger.info(f"Found {len(results)} docs for question '{query}'.")
            return results
        except Exception as error:
            self._logger.error("Error on search_documents", error)
            return []

    def format_context(self, documents: list[Document]) -> str:
        if not documents:
            return "No information in RAG db."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Неизвестный источник")
            chunk_id = doc.metadata.get("chunk_id", "N/A")

            context_parts.append(
                f"""
--- Документ {i} ---
Источник: {source}
Чанк: {chunk_id}
Содержание:
{doc.page_content}
"""
            )

        self._logger.debug(
            f"Prepared {len(context_parts)} context parts for {len(context_parts)} docs."
        )
        return "\n".join(context_parts)

    def ask(self, question: str, prompt: Prompts = Prompts.BASE):
        self._logger.info(f"Got {prompt.name} prompt with query: '{question}'.")
        documents = self.search_documents(question)
        context = self.format_context(documents)

        chain = (
            {"context": lambda x: x["context"], "question": lambda x: x["question"]}
            | self.prompts[prompt]
            | self.ollama
            | StrOutputParser()
        )

        response = chain.invoke({"context": context, "question": question})
        self._logger.info(f"Response: '{response}'.")

        return {
            "query": question,
            "prompt-type": prompt.value,
            "response": response,
            "context": context,
            "prompt": self.prompts[prompt].format(context=context, question=question),
            "sources": [
                {
                    "source": doc.metadata.get("source", "Неизвестный источник"),
                    "category": doc.metadata.get("category", "Неизвестная категория"),
                    "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                    "content_preview": f"{doc.page_content[:200]}...",
                }
                for doc in documents
            ],
            "num_sources": len(documents),
        }

    def _load_db(self, location: str | None = None):
        embeddings = HuggingFaceEmbeddings(
            model_name="all-mpnet-base-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        return FAISS.load_local(
            folder_path=location or self.faiss_db_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )

    def _connect_ollama(self, temperature):
        return OllamaLLM(
            model="llama3.1",
            temperature=temperature,
            num_predict=1024,
            # base_url="http://localhost:11434",
            # other params...
        )

    def _create_prompts(self) -> dict[Prompts, PromptTemplate]:
        base_prompt = PromptTemplate.from_file(
            os.path.join(self.current_dir, self.FILE_BASE_PROMPT),
            encoding="UTF-8",
            # input_variables=["context", "question"],
        )
        few_shot_prompt = PromptTemplate.from_file(
            os.path.join(self.current_dir, self.FILE_FEW_SHOT_PROMPT),
            encoding="UTF-8",
            # input_variables=["context", "question"],
        )
        cot_prompt = PromptTemplate.from_file(
            os.path.join(self.current_dir, self.FILE_COT_PROMPT),
            encoding="UTF-8",
            # input_variables=["context", "question"],
        )
        return {
            self.Prompts.BASE: base_prompt,
            self.Prompts.FEW_SHOT: few_shot_prompt,
            self.Prompts.COT: cot_prompt,
        }

    def _setup_logger(self, verbose):
        logging.basicConfig(
            filename=os.path.join(self.current_dir, "rag_bot.log"),
            format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
            level=logging.DEBUG if verbose else logging.INFO,
            encoding="utf-8",
            datefmt="%d-%m-%YT%H:%M:%S",
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)
        return logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="rag_client",
        description="RAG client for yarch07 project",
        epilog="Pass question about Warhammer 40000 fantasy world",
    )
    parser.add_argument("question", type=str, help="Query to RAG bot")
    parser.add_argument(
        "-d",
        "--documents",
        type=int,
        default=RAGBot.DEFAULT_MAX_DOCUMENTS,
        help="How many documents extract for RAG bot",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        choices=[el.value for el in RAGBot.Prompts],
        default=RAGBot.Prompts.BASE,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.question:
        bot = RAGBot(rag_max_results=args.documents, verbose=args.verbose)
        response = bot.ask(args.question, RAGBot.Prompts(args.prompt))
        print(response["response"])
