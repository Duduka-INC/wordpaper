from dataclasses import dataclass

from src.domain.operations.operation import Operation

@dataclass
class OperationPipeline:
    operations: list[Operation]

    def add(self, operation: Operation):
        self.operations.append(operation)

    def remove_at(self, index: int):
        self.operations.pop(index)

    def insert(self, operation: Operation, index: int):
        self.operations.insert(index, operation)

    def get_list(self):
        return self.operations