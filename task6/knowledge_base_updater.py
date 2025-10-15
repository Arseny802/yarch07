# update_index.py
import os
import logging
import git
from langchain.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename="update.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def clone_repo():
    try:
        repo = git.Repo.clone_from(
            "https://github.com/company/knowledge-base.git", "./docs"
        )
        logging.info("Репозиторий успешно клонирован")
        return repo
    except Exception as e:
        logging.error(f"Ошибка клонирования репозитория: {e}")
        raise


def load_documents():
    loader = GitLoader(repo_path="./docs", branch_name="main", file_suffix=".md")
    return loader.load()


def process_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return chunks


def update_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(
        documents=chunks, embedding=embeddings, persist_directory="./vector_store"
    )
    return vectorstore


def main():
    start_time = datetime.now()
    logging.info("Запуск обновления индекса")

    try:
        # Клонирование репозитория
        repo = clone_repo()

        # Загрузка документов
        docs = load_documents()
        logging.info(f"Загружено {len(docs)} документов")

        # Обработка документов
        chunks = process_documents(docs)
        logging.info(f"Создано {len(chunks)} чанков")

        # Обновление векторного индекса
        vectorstore = update_vector_store(chunks)
        logging.info("Индекс успешно обновлен")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logging.info(f"Обновление завершено за {duration:.2f} секунд")


if __name__ == "__main__":
    main()
