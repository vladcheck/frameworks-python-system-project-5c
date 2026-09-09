from Action import Action
from Menu import Menu

actions = [
    Action("0", "Выйти из приложения", Menu.menu_exit),
    Action("1", "Получить список выступлений", Menu.menu_get_performances),
    Action("2", "Создать выступление", Menu.menu_create_performance)
]


def print_menu():
    print("Выберите действие")
    for act in actions:
        print(f"{act.text}. {act.description.capitalize()}")
    print()


def main() -> None:
    while True:
        print_menu()

        actionText: str = input()

        for act in actions:
            if act.text == actionText:
                act.call()
                break
        else:
            print("Неверное действие")


if __name__ == "__main__":
    main()
