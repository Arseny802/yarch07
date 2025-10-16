import sys
import os
import csv
import random
import requests
import uuid
import json

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from task3.build_index import KnowledgeBaseIndexer
from task4.rag_bot import RAGBot


class CoverageTester:

    def __init__(self) -> None:
        self.bot = RAGBot(
            rag_max_results=40,
            temperature=0.01,
        )
        self.filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logs.csv"
        )
        self.csv_headers = [
            "timestamp",
            "query",
            "num_sources",
            "response_length",
            "success",
            "sources",
        ]
        with open(self.filepath, "w", encoding="utf-8") as file:
            csv.writer(file).writerow(self.csv_headers)

        self.test_data: dict[str, list[str]] = {
            "Сириус Блэк": ["эльдар"],
            "Копатыч": ["космодесантник", "капитан"],
            "Кар-Карыч": ["лидер", "хаос", "предатель"],
            "Чарли Уизли": ["лидер", "капеллан"],
            "Лунтик": ["бог", "божество", "император"],
            "Гэндальф": ["кровавые ангелы"],
            "Черепашки-Ниндзя": ["храмовники", "воины"],
        }
        self.success_counter = 0

    def make_request(self, search: str, expect_list: list[str]):
        response = self.bot.ask(f"Кто такой {search}?", RAGBot.Prompts.BASE)
        sources = response["sources"]
        self._write_log(
            response["timestamp"],
            response["query"],
            response["num_sources"],
            len(response["response"]),
            any(expect in response["response"].lower() for expect in expect_list),
            "\n".join([source["source"] for source in sources]),
        )

    def _write_log(
        self,
        timestamp,
        query: str,
        num_sources: int,
        response_length: int,
        success: bool,
        sources: str,
    ):
        if success:
            self.success_counter += 1
        with open(self.filepath, "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    timestamp,
                    query,
                    num_sources,
                    response_length,
                    success,
                    sources,
                ]
            )

    def make_success_calls(self):
        for key, val in self.test_data.items():
            self.make_request(key, val)

    def make_fail_calls(self):
        for key, val in self.test_data.items():
            self.make_request(val[0], [key])


if __name__ == "__main__":
    coverage_tester = CoverageTester()
    coverage_tester.make_success_calls()
    coverage_tester.make_fail_calls()
    print(
        f"Success points {coverage_tester.success_counter} / {len(coverage_tester.test_data)}"
    )
