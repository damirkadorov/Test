#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.tm Account Generator
Создание почтовых ящиков с паролем для API доступа
Сохранение в файл email:пароль
"""

import requests
import json
import random
import string
import time
import os
import sys

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mailtm_accounts.txt"
API_BASE = "https://api.mail.tm"
DOMAINS = ["mail.tm", "slmails.com", "czmail.com"]  # Доступные домены Mail.tm
DEFAULT_COUNT = 5
DELAY_BETWEEN = 2  # Секунд между созданием аккаунтов
# =====================================================

def generate_username(length=10):
    """Генерирует случайное имя пользователя"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_password(length=12):
    """Генерирует случайный пароль"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def get_domains():
    """Получает список доступных доменов Mail.tm"""
    try:
        response = requests.get(f"{API_BASE}/domains")
        if response.status_code == 200:
            domains = [d['domain'] for d in response.json()]
            return domains
    except:
        pass
    return DOMAINS

def create_account(domain=None, username=None, password=None):
    """
    Создаёт аккаунт на Mail.tm
    Возвращает словарь с email, password, token или None
    """
    if not domain:
        domains = get_domains()
        domain = random.choice(domains)
    
    if not username:
        username = generate_username()
    
    if not password:
        password = generate_password()
    
    email = f"{username}@{domain}"
    
    print(f"[*] Создаю: {email}")
    
    # Регистрация
    response = requests.post(
        f"{API_BASE}/accounts",
        json={
            "address": email,
            "password": password
        }
    )
    
    if response.status_code == 201:
        account_data = response.json()
        
        # Получаем токен для доступа к API
        token_response = requests.post(
            f"{API_BASE}/token",
            json={
                "address": email,
                "password": password
            }
        )
        
        token = None
        if token_response.status_code == 200:
            token = token_response.json().get("token")
        
        account = {
            "email": account_data['address'],
            "password": password,
            "id": account_data.get('id'),
            "token": token
        }
        
        print(f"[+] Создан: {account['email']}")
        print(f"[+] Пароль: {password}")
        
        return account
    
    elif response.status_code == 422:
        print(f"[-] Ошибка: email уже существует, пробуем другой...")
        return create_account(domain, generate_username(), password)
    else:
        print(f"[-] Ошибка: {response.status_code} - {response.text}")
        return None

def save_account(account, filename=OUTPUT_FILE):
    """Сохраняет аккаунт в файл (формат email:password)"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{account['email']}:{account['password']}\n")
    
    # Также сохраняем JSON с токеном (опционально)
    json_file = filename.replace('.txt', '.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
    except:
        accounts = []
    
    accounts.append({
        "email": account['email'],
        "password": account['password'],
        "id": account.get('id'),
        "token": account.get('token'),
        "created": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)

def get_messages(token, limit=10):
    """Получает список писем для аккаунта"""
    response = requests.get(
        f"{API_BASE}/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={"page": 1, "limit": limit}
    )
    
    if response.status_code == 200:
        return response.json()
    return []

def get_message_body(token, message_id):
    """Получает тело письма"""
    response = requests.get(
        f"{API_BASE}/messages/{message_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        return response.json()
    return None

def wait_for_code(token, sender_domain=None, timeout=60):
    """Ожидает письмо с кодом подтверждения (6 цифр)"""
    import re
    
    print(f"[*] Ожидание письма (макс {timeout} сек)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        messages = get_messages(token)
        
        if messages:
            for msg in messages:
                from_addr = msg.get('from', {}).get('address', '')
                
                if sender_domain and sender_domain not in from_addr:
                    continue
                
                msg_data = get_message_body(token, msg['id'])
                if msg_data:
                    body = msg_data.get('text', '')
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        code = match.group(1)
                        print(f"[+] Найден код: {code}")
                        return code
        
        time.sleep(5)
    
    print("[-] Код не получен за отведённое время")
    return None

def list_accounts(filename=OUTPUT_FILE):
    """Показывает все сохранённые аккаунты"""
    if not os.path.exists(filename):
        print("Файл с аккаунтами не найден")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        accounts = [line.strip() for line in f if line.strip()]
    
    print(f"\n📧 Сохранённые аккаунты ({len(accounts)}):")
    for i, acc in enumerate(accounts, 1):
        print(f"  {i}. {acc}")
    
    return accounts

def delete_account(account_id, token):
    """Удаляет аккаунт (если нужно)"""
    response = requests.delete(
        f"{API_BASE}/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 204

def main():
    print("=" * 60)
    print("Mail.tm Account Generator")
    print("=" * 60)
    
    # Показываем существующие аккаунты
    list_accounts()
    
    # Количество новых
    try:
        count = int(input(f"\nСколько аккаунтов создать (по умолч. {DEFAULT_COUNT}): ") or DEFAULT_COUNT)
    except:
        count = DEFAULT_COUNT
    
    print(f"\n[*] Будет создано {count} аккаунтов")
    print(f"[*] Задержка между созданием: {DELAY_BETWEEN} сек\n")
    
    created = 0
    for i in range(count):
        print(f"--- {i+1}/{count} ---")
        account = create_account()
        
        if account:
            save_account(account)
            created += 1
        else:
            print("[-] Ошибка создания, пропускаем...")
        
        if i < count - 1:
            time.sleep(DELAY_BETWEEN)
    
    print("\n" + "=" * 60)
    print(f"✅ Создано аккаунтов: {created}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

def console_mode():
    """Режим командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mail.tm Account Generator")
    parser.add_argument("-c", "--count", type=int, default=DEFAULT_COUNT, help="Количество аккаунтов")
    parser.add_argument("-o", "--output", default=OUTPUT_FILE, help="Файл для сохранения")
    parser.add_argument("--list", action="store_true", help="Показать сохранённые аккаунты")
    parser.add_argument("--domain", help="Использовать конкретный домен")
    parser.add_argument("--delay", type=int, default=DELAY_BETWEEN, help="Задержка между созданием (сек)")
    
    args = parser.parse_args()
    
    global OUTPUT_FILE, DELAY_BETWEEN
    OUTPUT_FILE = args.output
    DELAY_BETWEEN = args.delay
    
    if args.list:
        list_accounts(OUTPUT_FILE)
        return
    
    print(f"[*] Создание {args.count} аккаунтов...")
    
    for i in range(args.count):
        account = create_account(domain=args.domain)
        if account:
            save_account(account, args.output)
        if i < args.count - 1:
            time.sleep(DELAY_BETWEEN)
    
    print(f"\n✅ Сохранено в {args.output}")

if __name__ == "__main__":
    # Проверяем установку requests
    try:
        import requests
    except ImportError:
        print("Установите requests: pip install requests")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        console_mode()
    else:
        main()
