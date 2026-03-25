#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tuta (Tutanota) Account Generator
Регистрация без SMS, но с 48-часовой задержкой активации
"""

import time
import random
import string
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "tuta_accounts.txt"
TUTA_DOMAINS = ["tuta.com", "tutanota.com", "tutamail.com", "tuta.io", "keemail.me"]
DELAY_BETWEEN = 10
# =====================================================

def generate_username(length=12):
    """Генерирует случайное имя пользователя"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_password(length=14):
    """Генерирует надёжный пароль"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def generate_recovery_code():
    """Генерирует recovery-код Tuta (сохранить обязательно!)"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=16))

def register_tuta_account():
    """Регистрирует аккаунт Tuta через Selenium"""
    
    domain = random.choice(TUTA_DOMAINS)
    username = generate_username()
    email = f"{username}@{domain}"
    password = generate_password()
    recovery_code = generate_recovery_code()
    
    print(f"[*] Регистрация: {email}")
    
    options = Options()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Путь к chromedriver
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://app.tuta.com")
        time.sleep(3)
        
        wait = WebDriverWait(driver, 20)
        
        # Нажать "Sign up"
        signup_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up')]")))
        signup_btn.click()
        time.sleep(2)
        
        # Выбрать бесплатный тариф
        free_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Free')]")))
        free_btn.click()
        time.sleep(2)
        
        # Ввести email
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(1)
        
        # Выбрать домен (если нужно)
        try:
            domain_select = Select(driver.find_element(By.CSS_SELECTOR, "select"))
            domain_select.select_by_visible_text(domain)
        except:
            pass
        
        # Ввести пароль
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Подтверждение пароля
        confirm_field = driver.find_element(By.XPATH, "//input[@type='password'][2]")
        confirm_field.clear()
        confirm_field.send_keys(password)
        
        # Нажать "Next"
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]")))
        next_btn.click()
        time.sleep(3)
        
        # Сохранить recovery-код (Tuta показывает его после регистрации)
        print(f"[!] ВАЖНО: Сохраните recovery-код: {recovery_code}")
        
        # Завершение регистрации
        finish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Finish')]")))
        finish_btn.click()
        
        time.sleep(5)
        
        account = {
            "email": email,
            "password": password,
            "recovery_code": recovery_code,
            "domain": domain,
            "status": "pending_activation",  # 48h задержка
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
        f.write(f"{account['email']}:{account['password']}:{account['recovery_code']}\n")
        f.write(f"# Статус: {account['status']} - создан {account['created']}\n")
    
    print(f"[+] Сохранён: {account['email']}")
    print(f"[+] Recovery: {account['recovery_code']}")

def main():
    print("=" * 60)
    print("Tuta (Tutanota) Account Generator")
    print("ВНИМАНИЕ: После регистрации требуется 48 часов для активации!")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    for i in range(count):
        print(f"\n--- {i+1}/{count} ---")
        account = register_tuta_account()
        if account:
            save_account(account)
        else:
            print("[-] Ошибка регистрации")
        
        if i < count - 1:
            time.sleep(DELAY_BETWEEN)
    
    print("\n" + "=" * 60)
    print("✅ Генерация завершена")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("⚠️ Аккаунты активируются через 48 часов!")
    print("=" * 60)

if __name__ == "__main__":
    main()
