
import json
import math
from pathlib import Path


class LocalVectorStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.records = []

    @staticmethod
    def _validate_record(record: dict) -> None:
        if not isinstance(record, dict):
            raise ValueError(
                "Each vector store record must be a dictionary."
            )

        chunk = record.get("chunk")
        embedding = record.get("embedding")

        if not isinstance(chunk, dict):
            raise ValueError(
                "Each record must contain a valid chunk."
            )

        if not isinstance(embedding, (list, tuple)):
            raise ValueError(
                "Embedding must be a list or tuple."
            )

        if not embedding:
            raise ValueError(
                "Embedding cannot be empty."
            )

        try:
            valid_embedding = all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in embedding
            )
        except (TypeError, OverflowError):
            valid_embedding = False

        if not valid_embedding:
            raise ValueError(
                "Embedding must contain only finite numeric values."
            )

    @classmethod
    def _validate_dimensions(cls, records: list[dict]) -> None:
        expected_dimension = None

        for record in records:
            cls._validate_record(record)

            dimension = len(record["embedding"])

            if expected_dimension is None:
                expected_dimension = dimension
            elif dimension != expected_dimension:
                raise ValueError(
                    "Embedding dimensions must be consistent "
                    "across all records."
                )

    def add(
        self,
        chunk: dict,
        embedding: list[float]
    ) -> None:
        record = {
            "chunk": chunk,
            "embedding": embedding
        }

        self._validate_dimensions(
            self.records + [record]
        )
        self.records.append(record)

    def save(self) -> None:
        self._validate_dimensions(self.records)

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
                ensure_ascii=False,
                allow_nan=False
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

        self._validate_dimensions(data)

        self.records = data

    def count(self) -> int:
        return len(self.records)
