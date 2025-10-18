#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from build_index import KnowledgeBaseIndexer


def search_example(test_queries: list[str] | None = None):
    if not test_queries:
        return

    faiss_index = KnowledgeBaseIndexer().create_faiss_index()

    for query in test_queries:
        print(f"query: {query}")
        results = faiss_index.similarity_search(query, k=3)

        for i, result in enumerate(results, 1):
            print(f"Source {i}. {result.metadata['source']}:")
            print(f"{result.page_content[:300]}...\n\n")


if __name__ == "__main__":
    test_queries = [
        "Кто такой Лунтик?",
        "Что такое Слизерин?",
        "Расскажи о битве на Терре с Кар-Карычем",
        "Чем известны Уизли?",
        "Стоит ли связываться с Долорес Амбридж?",
        "Какие есть изветные Боги?",
    ]

    search_example(test_queries)
