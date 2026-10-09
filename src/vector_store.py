import json
from pathlib import Path


class LocalVectorStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.records = []

    def add(
        self,
        chunk: dict,
        embedding: list[float]
    ) -> None:

        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        record = {
            "chunk": chunk,
            "embedding": embedding
        }

        self.records.append(record)

    def save(self) -> None:
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.storage_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.records,
                file,
                indent=4,
                ensure_ascii=False
            )

    def load(self) -> None:
        if not self.storage_path.exists():
            self.records = []
            return

        with self.storage_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "Vector store must contain a list."
            )

        self.records = data

    def count(self) -> int:
        return len(self.records)