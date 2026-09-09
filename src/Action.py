from types import FunctionType


class Action:
    text: str
    description: str
    execute: FunctionType

    def __init__(self,text,description,execute) -> None:
        self.text = text
        self.description = description
        self.execute = execute

    def call(self, *args, **kwargs):
        self.execute(*args, **kwargs)
        print()
