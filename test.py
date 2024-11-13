import vk_api
import time
from datetime import datetime, timedelta
from plyer import notification
import winsound
import os

import requests

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Сообщение успешно отправлено.")
    else:
        print(f"Ошибка отправки сообщения: {response.status_code}")
        print(response.text)

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, 'CHAT_ID' - на ID чата
bot_token = '7764571029:AAEZYDDuJ_fqc3a78hOeFXZR840TRKEjp1Q'
chat_id = '1430123700'

# Вставьте ваш токен доступа
access_token = [
    "vk1.a.yn8Yo2-VI9diYtdhNgCYHX2RDxQU6zAZK_q2ai3_VOpihcIBopiz6nPs-AU8u4BmkByRgyz2o4fQS7hH69WcNg2aFV1jmBTw-plZj0LNwtVETLjotg03Vy0TC2UXE-usHFb_eU7MYZV-XdIL5HO-T3MwFZdIjBVa-Y5GG2HVPh-M43VMdQk_C-HcQfjhJ0OVgAoGo9TVk9e3MP5QATlMmQ"
]

# Список групп для мониторинга (ID или короткие имена)
groups = []

# Ключевые слова для поиска
keywords = []

# Задержка между запросами (в секундах)
delay = 60

print(os.getcwd())

# Путь к файлу для хранения ID постов
seen_posts_file = "D:\\projects\\pyton_tests\\tests\\parser\\seen_posts.txt"
keywords_file = "D:\\projects\\pyton_tests\\tests\\parser\\keywords.txt"
days_gone_file = "D:\\projects\\pyton_tests\\tests\\parser\\days_gone.txt"
groups_file = "D:\\projects\\pyton_tests\\tests\\parser\\groups.txt"

def load_list(file):
    """Загружает список string из файла"""
    if os.path.exists(file):
        with open(file, "r") as file:
            return set(line.strip() for line in file)
    return set()

def load_int(file):
    """Загружает int из файла"""
    if os.path.exists(file):
        with open(file, "r") as f:
            line = f.readline().strip()
            return int(line) if line.isdigit() else 0
    return 0

def save_seen_posts(seen_posts):
    """Сохраняет список ID постов, которые были обработаны."""
    with open(seen_posts_file, "w") as file:
        for post_id in seen_posts:
            file.write(f"{post_id}\n")

# # Звуковой сигнал
# def play_sound():
#     winsound.Beep(1000, 500)  # Частота 1000 Гц, длительность 500 мс

def show_notification(group, keyword, post, group_id):
    """Отправляет уведомление в telegram."""
    # text = post['text'][:100] + '...' if len(post['text']) > 100 else post['text']
    text = f"Найден пост с ключевым словом '{keyword}' в группе {group}:\n"
    text += f"Ссылка на пост: https://vk.com/wall-{group_id}_{post['id']}\n"
    text += f"Текст поста: {post['text']}"

    send_message(bot_token, chat_id, text)

    print()
    print(f"Найден пост с ключевым словом '{keyword}' в группе {group}:")
    print(f"Ссылка на пост: https://vk.com/wall-{group_id}_{post['id']}")
    print("Текст поста:")
    print(post['text'])
    print()
    print("-" * 50)

def get_current_timestamp():
    """Функция для получения текущего времени в формате Unix timestamp"""
    return int(time.mktime(datetime.now().timetuple()))

def search_posts(group_id, keyword, vk):
    """Функция для поиска постов по ключевым словам в группе за текущую дату"""
    response = vk.wall.search(owner_id=f"-{group_id}", query=keyword, count=10)
    return response['items']

def monitor():
    """Основная функция мониторинга"""
    current_timestamp = get_current_timestamp()
    day_gone = load_int(days_gone_file)
    start_of_day = int(time.mktime((datetime.now() - timedelta(days=day_gone)).replace(hour=0, minute=0, second=0, microsecond=0).timetuple()))
    seen_posts = load_list(seen_posts_file)

    while True:
        groups = load_list(groups_file)

        for group in groups:
            for access in access_token:
                try:
                    vk_session = vk_api.VkApi(token=access)
                    vk = vk_session.get_api()
                    group_info = vk.groups.getById(group_ids=group)[0]
                    group_id = group_info['id']

                    keywords = load_list(keywords_file)

                    for keyword in keywords:
                        posts = search_posts(group_id, keyword, vk)

                        for post in posts:
                            post_link = f"https://vk.com/wall-{group_id}_{post['id']}"
                            if (keyword.lower() in post['text'].lower() and 
                                post['date'] > start_of_day and 
                                post_link not in seen_posts):
                                
                                seen_posts.add(post_link)
                                show_notification(group, keyword, post, group_id)

                    break
                except Exception as e:
                    print(f"Ошибка при мониторинге группы {group}: {e}")
            print(group + " завершена")

        save_seen_posts(seen_posts)
        print("=-=-=-=-=-=-=-=-=-=")
        time.sleep(delay)

if __name__ == "__main__":
    monitor()
