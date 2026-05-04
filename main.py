import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

FAVORITES_FILE = 'favorites.json'
GITHUB_API_URL = 'https://api.github.com/search/users'

# Загрузка избранных пользователей
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохранение избранных пользователей
def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

# Поиск пользователей на GitHub
def search_github_users(query):
    try:
        response = requests.get(GITHUB_API_URL, params={'q': query})
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить запрос: {e}")
        return []

# Обновление списка пользователей в GUI
def update_user_list():
    query = entry_search.get().strip()
    if not query:
        messagebox.showwarning("Внимание", "Поле поиска не должно быть пустым.")
        return

    users = search_github_users(query)
    tree.delete(*tree.get_children())
    for user in users:
        login = user['login']
        avatar_url = user['avatar_url']
        # Для простоты не загружаем аватарки в этом примере
        tree.insert('', 'end', values=(login, avatar_url))

# Добавление пользователя в избранное
def add_to_favorites():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Внимание", "Выберите пользователя из списка.")
        return

    login = tree.item(selected, 'values')[0]
    if login in [u['login'] for u in favorites]:
        messagebox.showinfo("Информация", "Пользователь уже в избранном.")
        return

    # Получаем полную информацию о пользователе
    try:
        user_info = requests.get(f'https://api.github.com/users/{login}').json()
        favorites.append(user_info)
        save_favorites(favorites)
        messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}")

# Инициализация избранных пользователей
favorites = load_favorites()

# Создание окна
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("600x400")

# Поле поиска и кнопка
frame_search = tk.Frame(root)
frame_search.pack(pady=10, fill=tk.X)

entry_search = tk.Entry(frame_search, width=50)
entry_search.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_search = tk.Button(frame_search, text="Поиск", command=update_user_list)
btn_search.pack(side=tk.LEFT, padx=5)

# Таблица результатов
tree = ttk.Treeview(root, columns=("Логин", "Аватар"), show="headings")
tree.heading("Логин", text="Логин")
tree.heading("Аватар", text="Аватар")
tree.column("Логин", width=200)
tree.column("Аватар", width=100)
tree.pack(expand=True, fill=tk.BOTH, pady=5)

# Кнопка добавления в избранное
btn_fav = tk.Button(root, text="Добавить в избранное", command=add_to_favorites)
btn_fav.pack(pady=10)

root.mainloop()