#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator
Полная автоматическая регистрация с ручным решением hCaptcha
"""

import time
import random
import string
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
DELAY_STEP = 5  # Задержка 5 секунд между шагами
DELAY_AFTER_CLICK = 7  # Задержка после кликов
# =====================================================

# Реалистичные имена для генерации
FIRST_NAMES = [
    "mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", 
    "rain", "silja", "marten", "merle", "andres", "triin", "priit"
]

LAST_NAMES = [
    "jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", 
    "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"
]

def generate_username():
    """Генерирует реалистичное имя пользователя типа marijari1999"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    year = random.randint(1950, 2005)
    # Варианты: marijari1999, mari.jari1999, mari_jari1999
    style = random.choice(['', '.', '_'])
    if style:
        username = f"{first}{style}{last}{year}"
    else:
        username = f"{first}{last}{year}"
    return username.lower()

def generate_password(length=14):
    """Генерирует надёжный пароль"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def get_chromedriver_path():
    """Находит путь к chromedriver"""
    possible_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        os.path.expanduser("~") + "/.local/bin/chromedriver",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def register_mail_ee():
    """Регистрирует ящик на Mail.ee"""
    
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    options = Options()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Используем системный chromedriver
    driver_path = get_chromedriver_path()
    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        print("[-] chromedriver не найден! Установите: sudo apt install chromium-driver")
        return None
    
    try:
        # Шаг 1: Открыть страницу регистрации
        driver.get("https://login.mail.ee/signup?go=portal")
        print("[1] Открыта страница регистрации")
        time.sleep(5)
        
        wait = WebDriverWait(driver, 20)
        
        # Шаг 2: Принять куки (кнопка "Nõustun")
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nõustun')]")))
            cookie_btn.click()
            print("[2] Приняты куки (Nõustun)")
            time.sleep(DELAY_AFTER_CLICK)
        except:
            print("[2] Кнопка куки не найдена, продолжаем...")
        
        # Шаг 3: Ввести имя пользователя
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys(username)
        print(f"[3] Введено имя: {username}")
        time.sleep(DELAY_STEP)
        
        # Шаг 4: Нажать "Kontrolli saadavust" (проверить доступность)
        check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontrolli saadavust')]")))
        check_btn.click()
        print("[4] Нажата кнопка Kontrolli saadavust")
        time.sleep(DELAY_AFTER_CLICK)
        
        # Проверка, что имя доступно
        try:
            error_msg = driver.find_element(By.XPATH, "//div[contains(text(), 'pole saadaval')]")
            if error_msg.is_displayed():
                print("[-] Имя занято, пробуем другое...")
                return None
        except:
            pass
        
        # Шаг 5: Ввести пароль
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.clear()
        password_field.send_keys(password)
        print("[5] Пароль введён")
        time.sleep(DELAY_STEP)
        
        # Шаг 6: Поставить две галочки (условия)
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for i, cb in enumerate(checkboxes):
            if not cb.is_selected():
                cb.click()
                print(f"[6] Отмечена галочка {i+1}")
                time.sleep(2)
        
        # Шаг 7: Нажать "Loo uus konto" (создать аккаунт)
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Loo uus konto')]")))
        create_btn.click()
        print("[7] Нажата кнопка Loo uus konto")
        time.sleep(5)
        
        # Шаг 8: Ожидание hCaptcha (ручное решение)
        print("\n" + "!" * 50)
        print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ В ОТКРЫТОМ БРАУЗЕРЕ")
        print("!" * 50)
        input("Нажмите Enter ПОСЛЕ решения капчи и завершения регистрации...")
        
        # Проверка успешности
        current_url = driver.current_url
        if "login" in current_url or "portal" in current_url:
            print("[+] Регистрация успешна!")
            
            # Включаем IMAP/POP3 доступ
            print("[*] Включаю IMAP/POP3 доступ...")
            try:
                driver.get("https://login.mail.ee/settings")
                time.sleep(3)
                
                enable_imap = driver.find_element(By.XPATH, "//input[@type='checkbox' and contains(@name, 'pop3')]")
                if not enable_imap.is_selected():
                    enable_imap.click()
                    save_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
                    save_btn.click()
                    print("[+] IMAP/POP3 включён")
                    time.sleep(3)
            except Exception as e:
                print(f"[!] Не удалось включить IMAP: {e}")
            
            account = {
                "email": email,
                "password": password,
                "username": username,
                "imap_server": "mail.ee",
                "imap_port": 993,
                "smtp_server": "mail.ee",
                "smtp_port": 587,
                "created": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return account
        else:
            print("[-] Возможно, ошибка регистрации")
            return None
        
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return None
    finally:
        driver.quit()

def save_account(account):
    """Сохраняет аккаунт в файл"""
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{account['email']}:{account['password']}\n")
        f.write(f"# IMAP: {account['imap_server']}:{account['imap_port']} (SSL)\n")
        f.write(f"# SMTP: {account['smtp_server']}:{account['smtp_port']} (TLS)\n")
        f.write(f"# Создан: {account['created']}\n")
        f.write("-" * 40 + "\n")
    
    print(f"[+] Сохранён: {account['email']}")

def main():
    print("=" * 60)
    print("Mail.ee Account Generator")
    print("Регистрация почтовых ящиков с IMAP/SMTP")
    print("=" * 60)
    print("\n⚠️ ВНИМАНИЕ:")
    print("   - hCaptcha решается ВРУЧНУЮ")
    print("   - После каждого шага задержка 5-7 секунд")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    for i in range(count):
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        account = register_mail_ee()
        if account:
            save_account(account)
        else:
            print("[-] Ошибка регистрации, пропускаем...")
        
        if i < count - 1:
            print(f"\n[*] Ожидание {DELAY_AFTER_CLICK} секунд...")
            time.sleep(DELAY_AFTER_CLICK)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Сохранено в {OUTPUT_FILE}")
    print("\n📧 Настройки IMAP/SMTP:")
    print("   IMAP: mail.ee:993 (SSL)")
    print("   SMTP: mail.ee:587 (TLS)")
    print("=" * 60)

if __name__ == "__main__":
    main()
