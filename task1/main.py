import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import argparse
import os
import logging


# Створення логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Формат логів
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Хендлер для файлу
file_handler = logging.FileHandler('task1_logfile.log', encoding='utf-8')
file_handler.setFormatter(formatter)

# Хендлер для консолі
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Додавання обох хендлерів
logger.addHandler(file_handler)
logger.addHandler(console_handler)


async def read_folder(source, dest):
    tasks = []
    try:
        async for item in source.iterdir():
            if await item.is_dir():
                await read_folder(item, dest)
            else:
                tasks.append(copy_file(item, dest))

    except Exception as e:
        logger.error(f"{e}")

    await asyncio.gather(*tasks)


async def copy_file(file_path, dest):
    try:
        ext = file_path.suffix[1:] if file_path.suffix else "no_extension"
        ext_dir = dest/ext
        await ext_dir.mkdir(parents=True, exist_ok=True)
        await copyfile(file_path, ext_dir/file_path.name)

    except Exception as e:
        logger.error(f"{e}")


async def main():
    # Парсер для аргументів командного рядка
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширенням"
    )
    parser.add_argument(
        "--source", "-s", required=True, type=str, help="Шлях до вихідної папки"
    )
    parser.add_argument(
        "--dest", "-d", required=True, type=str, help="Шлях до цільової папки"
    )
    args = parser.parse_args()

    # Ініціалізація асинхронних шляхів для вихідної та цільової папок.
    source_path = AsyncPath(args.source)
    dest_path = AsyncPath(args.dest)

    # Перевірка існування вихідної папки
    if not await source_path.exists():
        print(f"[ERROR] Відсутня вихідна папка '{source_path}'")
        return

    # Якщо цільова папка не існує то створюється
    await dest_path.mkdir(exist_ok=True, parents=True)

    # Запуск рекурсивного обходу та копіюванння
    await read_folder(source_path, dest_path)

    logger.info('Програма завершена. Всі файли скопійовано без помилок')


if __name__ == "__main__":
    asyncio.run(main())


# python main.py --source ../venv --dest ./dest
