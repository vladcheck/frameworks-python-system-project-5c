from typing import List

from User import User

class Performance:
  name: str
  participants: List[User]

  def __init__(self, name: str):
    self.name = name

  def __str__(self) -> str:
    return self.name