from typing import List, NoReturn

from entities.Performance import Performance
from api import get_performances, add_new_performance


class Menu:
    @staticmethod
    def menu_exit() -> NoReturn:
        print("Хорошего дня!")
        exit(0)

    @staticmethod
    def menu_get_performances():
        perfs: List[Performance] = get_performances()

        if len(perfs) == 0:
            print("Выступлений нет.")
            return

        print("Выступления")
        for p in perfs:
            print(f"- {p}")

    @staticmethod
    def menu_create_performance():
        name = input("Введите название выступления\n")
        add_new_performance(name)
        print("Выступление создано")
