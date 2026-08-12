from typing import List

from airplanes import Aeroplane
from core import AeroplanesAPI
from storage import JSONSaver


def filter_aeroplanes(planes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    """
    Фильтрует список самолётов по странам регистрации.

    Сравнение выполняется регистронезависимо, пустые строки игнорируются.

    Args:
        planes: Список объектов Aeroplane.
        countries: Список названий стран для фильтрации.

    Returns:
        Отфильтрованный список самолётов.
    """
    if not countries:
        return planes
    countries_lower = [c.strip().lower() for c in countries if c.strip()]
    return [p for p in planes if p.origin_country.lower() in countries_lower]


def get_aeroplanes_by_altitude(
    planes: List[Aeroplane], min_alt: float, max_alt: float
) -> List[Aeroplane]:
    """
    Фильтрует самолёты по диапазону высоты полёта.

    Использует поле geo_altitude. Границы диапазона включаются.

    Args:
        planes: Список объектов Aeroplane.
        min_alt: Минимальная высота (м).
        max_alt: Максимальная высота (м).

    Returns:
        Список самолётов, попадающих в указанный диапазон высот.
    """
    return [p for p in planes if min_alt <= p.geo_altitude <= max_alt]


def sort_aeroplanes(planes: List[Aeroplane]) -> List[Aeroplane]:
    """
    Сортирует самолёты по высоте полёта (по убыванию).

    Сортировка опирается на реализацию __gt__ в классе Aeroplane.

    Args:
        planes: Список объектов Aeroplane.

    Returns:
        Отсортированный список самолётов (от большей высоты к меньшей).
    """
    return sorted(planes, reverse=True)


def get_top_aeroplanes(planes: List[Aeroplane], n: int) -> List[Aeroplane]:
    """
    Возвращает топ‑N самолётов из отсортированного списка.

    Если n <= 0, возвращается пустой список. Если n больше длины списка,
    возвращается весь список.

    Args:
        planes: Отсортированный список объектов Aeroplane.
        n: Количество самолётов для выборки.

    Returns:
        Список из N первых самолётов.
    """
    if n <= 0:
        return []
    return planes[:n]


def print_aeroplanes(planes: List[Aeroplane]) -> None:
    """
    Выводит таблицу с данными о самолётах в консоль.

    Отображает номер, позывной, страну, высоту и скорость.
    Если список пуст — выводит сообщение об отсутствии данных.

    Args:
        planes: Список объектов Aeroplane для вывода.
    """
    if not planes:
        print("\nНет данных для отображения.")
        return

    print(
        f"\n{'№':<3} {'Callsign':<12} {'Страна':<15} {'Высота (м)':<14} {'Скорость (м/с)':<14}"
    )
    print("-" * 65)
    for i, p in enumerate(planes, 1):
        print(
            f"{i:<3} {p.callsign:<12} {p.origin_country:<15} "
            f"{p.geo_altitude:>12.1f} {p.velocity:>14.1f}"
        )
    print("-" * 65)


def parse_altitude_range(range_str: str):
    """
    Парсит строку с диапазоном высот и возвращает (min, max).

    Поддерживает форматы: '10000', '5000 - 10000'. Если порядок min/max перепутан,
    значения автоматически меняются местами. При ошибке возвращается полный диапазон.

    Args:
        range_str: Строка с диапазоном (может быть пустой).

    Returns:
        Кортеж (min_alt, max_alt). Если ввод некорректен, min=0, max=inf.
    """
    range_str = range_str.strip()
    if not range_str:
        return 0.0, float("inf")

    parts = [p.strip() for p in range_str.split("-")]
    try:
        if len(parts) == 1:
            val = float(parts[0])
            return val, val
        elif len(parts) == 2:
            min_val = float(parts[0]) if parts[0] else 0.0
            max_val = float(parts[1]) if parts[1] else float("inf")
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            return min_val, max_val
        else:
            raise ValueError
    except ValueError:
        print("Некорректный формат диапазона высот. Используем полный диапазон.")
        return 0.0, float("inf")


def user_interaction():
    """
    Основная точка взаимодействия с пользователем.

    Запрашивает у пользователя страну, количество самолётов для топа,
    фильтры по странам и диапазон высот, затем выводит итоговую таблицу
    и статистику.

    Обрабатывает ошибки API и некорректный ввод, использует данные
    из хранилища при сбоях.
    """
    api = AeroplanesAPI(storage_path="../data/airplanes.json")
    saver = JSONSaver("../data/airplanes.json")

    print("=== Авиа‑мониторинг: консоль (ООП‑версия) ===")

    country = input(
        "\nВведите название страны для получения данных о самолётах (например: Spain, Italy, Portugal): "
    ).strip()
    aeroplanes: List[Aeroplane] = []

    if country:
        try:
            print(f"Запрос данных для страны: {country}...")
            aeroplanes = api.get_aeroplanes(country)
            print(f"Успешно получено и сохранено самолётов: {len(aeroplanes)}")
        except ValueError as e:
            print(f"Ошибка: {e}")
            aeroplanes = saver.get_all_as_objects()
        except RuntimeError as e:
            print(f"Произошла ошибка при запросе к API: {e}")
            aeroplanes = saver.get_all_as_objects()
    else:
        print("Страна не указана. Работаем с данными из хранилища.")
        aeroplanes = saver.get_all_as_objects()

    if not aeroplanes:
        print(
            "В хранилище нет данных о самолётах. Попробуйте ввести корректное название страны."
        )
        return

    while True:
        n_input = input(
            "Введите количество самолётов для вывода в топ N (целое число > 0): "
        ).strip()
        try:
            n = int(n_input)
            if n > 0:
                break
            else:
                print("Число должно быть больше 0.")
        except ValueError:
            print("Пожалуйста, введите корректное целое число.")

    filter_words_input = input(
        "Введите названия стран для фильтрации по стране регистрации (через пробел, можно оставить пустым): "
    ).strip()
    filter_words = filter_words_input.split() if filter_words_input else []

    altitude_range_input = input(
        "Введите диапазон высот полёта (формат: min - max, например '10000 - 15000', можно оставить пустым): "
    ).strip()
    min_alt, max_alt = parse_altitude_range(altitude_range_input)

    filtered_aeroplanes = filter_aeroplanes(aeroplanes, filter_words)
    ranged_aeroplanes = get_aeroplanes_by_altitude(
        filtered_aeroplanes, min_alt, max_alt
    )
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, n)

    print_aeroplanes(top_aeroplanes)

    print(f"\nВсего в хранилище: {len(aeroplanes)}")
    print(f"После фильтра по странам: {len(filtered_aeroplanes)}")
    print(f"В диапазоне высот: {len(ranged_aeroplanes)}")
    print(f"Отображено в топе: {len(top_aeroplanes)}")


if __name__ == "__main__":
    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")
