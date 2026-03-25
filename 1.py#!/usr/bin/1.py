#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
99mail.us Email Generator
Простая генерация временных почтовых ящиков
"""

import random
import string
import time
import os

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "generated_emails.txt"
DOMAINS = ["99mail.us", "99mail.info", "99mail.org"]  # Дополнительные домены, если есть
COUNT = 10  # Количество генерируемых ящиков по умолчанию
# =====================================================

def generate_username(length=10):
    """Генерирует случайное имя пользователя"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_email(domain=None, username=None):
    """Генерирует email на 99mail.us"""
    if not domain:
        domain = "99mail.us"
    
    if not username:
        username = generate_username()
    
    return f"{username}@{domain}"

def generate_batch(count=10, domains=None):
    """Генерирует пакет email-адресов"""
    if not domains:
        domains = DOMAINS
    
    emails = []
    for _ in range(count):
        domain = random.choice(domains)
        email = generate_email(domain)
        emails.append(email)
    
    return emails

def save_to_file(emails, filename=OUTPUT_FILE):
    """Сохраняет email-адреса в файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        for email in emails:
            f.write(email + '\n')
    print(f"[+] Сохранено {len(emails)} адресов в {filename}")

def load_emails(filename=OUTPUT_FILE):
    """Загружает email-адреса из файла"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_with_custom_usernames(usernames, domain="99mail.us"):
    """Генерирует email-адреса из списка имён пользователей"""
    emails = [f"{username}@{domain}" for username in usernames]
    return emails

def main():
    print("=" * 50)
    print("99mail.us Email Generator")
    print("=" * 50)
    
    # Генерация
    count = int(input(f"Количество адресов (по умолчанию {COUNT}): ") or COUNT)
    
    print(f"\n[*] Генерация {count} адресов...")
    emails = generate_batch(count)
    
    # Показываем результат
    print("\n📧 Сгенерированные адреса:")
    for i, email in enumerate(emails, 1):
        print(f"  {i}. {email}")
    
    # Сохраняем
    save_to_file(emails)
    
    print(f"\n✅ Готово! Всего сгенерировано: {len(emails)}")
    print(f"📁 Файл: {OUTPUT_FILE}")

def console_mode():
    """Консольный режим с аргументами командной строки"""
    import argparse
    
    parser = argparse.ArgumentParser(description="99mail.us Email Generator")
    parser.add_argument("-c", "--count", type=int, default=10, help="Количество адресов")
    parser.add_argument("-o", "--output", default=OUTPUT_FILE, help="Файл для сохранения")
    parser.add_argument("-d", "--domain", default="99mail.us", help="Домен (по умолчанию 99mail.us)")
    parser.add_argument("-p", "--prefix", help="Префикс для email (без @domain)")
    parser.add_argument("--list", action="store_true", help="Показать все сохранённые адреса")
    
    args = parser.parse_args()
    
    if args.list:
        emails = load_emails(args.output)
        print(f"\n📧 Сохранённые адреса ({len(emails)}):")
        for email in emails:
            print(f"  {email}")
        return
    
    # Генерация
    if args.prefix:
        email = f"{args.prefix}@{args.domain}"
        emails = [email]
    else:
        emails = generate_batch(args.count, [args.domain])
    
    # Показываем
    print(f"\n📧 Сгенерированные адреса ({len(emails)}):")
    for email in emails:
        print(f"  {email}")
    
    # Сохраняем (добавляем в конец файла)
    with open(args.output, 'a', encoding='utf-8') as f:
        for email in emails:
            f.write(email + '\n')
    
    print(f"\n✅ Сохранено в {args.output}")

if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        console_mode()
    else:
        main()
