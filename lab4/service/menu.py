from model.dish import Dish


class Menu:
    def __init__(self) -> None:
        self._dishes: list[Dish] = []

    def add_dish(self, dish: Dish) -> None:
        if dish is None:
            raise ValueError("Страва не може бути None")
        self._dishes.append(dish)

    def remove_dish(self, dish: Dish) -> bool:
        try:
            self._dishes.remove(dish)
            return True
        except ValueError:
            return False

    def contains_dish(self, dish: Dish) -> bool:
        return dish in self._dishes

    def get_dishes(self) -> list[Dish]:
        return list(self._dishes)

    def is_empty(self) -> bool:
        return len(self._dishes) == 0

    def __len__(self) -> int:
        return len(self._dishes)

    def __repr__(self) -> str:
        return f"Menu(dishes={len(self._dishes)})"
