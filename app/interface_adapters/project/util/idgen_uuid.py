import uuid

from app.application.project.ports import IdGenerator


class UUIDGenerator(IdGenerator):
    def generate(self) -> str:
        return uuid.uuid4().hex
