from typing import NamedTuple, Callable


def catch_all_exceptions(msg: str):
    def real_decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IndexError as e:
                print(f"Проблема с разделителем строки из раздела {msg}. Он не найден или список пуст.")
            except Exception as e:
                print(f"Какая-то ошибка с delimetr из раздела {msg}")

        return wrapper

    return real_decorator
