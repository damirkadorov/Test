#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator
Создание почтовых ящиков с IMAP/SMTP доступом для ChatGPT
Регистрация без SMS
"""

import time
import random
import string
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
DELAY_BETWEEN = 10
MAIL_EE_URL = "https://www.mail.ee"
# =====================================================

def generate_username(length=10):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_password(length=14):
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
    
    print(f"[*] Регистрация: {email}")
    
    options = Options()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Используем системный chromedriver
    driver_path = get_chromedriver_path()
    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        print("[-] chromedriver не найден! Установите: sudo apt install chromium-driver")
        return None
    
    try:
        driver.get(MAIL_EE_URL)
        print("[*] Открыта страница Mail.ee")
        time.sleep(3)
        
        wait = WebDriverWait(driver, 30)
        
        # Нажимаем "Регистрация" / "Sign up"
        try:
            signup_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Регистрация')] | //a[contains(text(), 'Sign up')]")
            ))
            signup_btn.click()
            print("[*] Нажата кнопка регистрации")
            time.sleep(2)
        except:
            print("[*] Ищу форму регистрации...")
        
        # Поле имени пользователя
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys(username)
        time.sleep(1)
        
        # Поле пароля
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        
        # Подтверждение пароля
        confirm_field = driver.find_element(By.NAME, "password2")
        confirm_field.send_keys(password)
        
        # CAPTCHA (ручное решение)
        print("[!] Решите CAPTCHA вручную в открытом браузере...")
        input("Нажмите Enter после решения CAPTCHA...")
        
        # Кнопка регистрации
        register_btn = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
        register_btn.click()
        
        time.sleep(5)
        
        # Проверка успешности
        if "error" in driver.current_url.lower():
            print("[-] Ошибка регистрации")
            return None
        
        # Включаем IMAP/POP3 доступ (важно для автоматизации!)
        print("[*] Включаю IMAP/POP3 доступ...")
        try:
            # Переходим в настройки
            settings_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Settings')] | //a[contains(text(), 'Настройки')]")
            ))
            settings_link.click()
            time.sleep(2)
            
            # Находим опцию "Enable external POP3/IMAP and SMTP access"
            enable_checkbox = driver.find_element(By.XPATH, 
                "//input[@type='checkbox' and contains(@value, 'pop3')] | //input[@value='enable_pop3']")
            if not enable_checkbox.is_selected():
                enable_checkbox.click()
                print("[*] Включён внешний доступ (IMAP/POP3)")
            
            # Сохраняем настройки
            save_btn = driver.find_element(By.XPATH, "//input[@type='submit'] | //button[@type='submit']")
            save_btn.click()
            print("[*] Настройки сохранены")
            time.sleep(2)
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
    print("Поддержка IMAP/SMTP для ChatGPT")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    for i in range(count):
        print(f"\n--- {i+1}/{count} ---")
        account = register_mail_ee()
        if account:
            save_account(account)
        else:
            print("[-] Ошибка регистрации")
        
        if i < count - 1:
            time.sleep(DELAY_BETWEEN)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Сохранено в {OUTPUT_FILE}")
    print("\n📧 Настройки IMAP для почтовой программы:")
    print("   IMAP сервер: mail.ee")
    print("   IMAP порт: 993 (SSL)")
    print("   SMTP сервер: mail.ee")
    print("   SMTP порт: 587 (TLS) или 465 (SSL)")
    print("=" * 60)

if __name__ == "__main__":
    main()
