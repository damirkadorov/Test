#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator
Работает на Python 3.12 без distutils
Использует обычный Selenium + ручное решение Cloudflare и hCaptcha
"""

import time
import random
import string
import os
import sys
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
DELAY_STEP = 5
DELAY_AFTER_CLICK = 7
# =====================================================

# Реалистичные имена
FIRST_NAMES = ["mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", "rain", "silja", "marten", "merle", "andres", "triin", "priit"]
LAST_NAMES = ["jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"]

def generate_username():
    """Генерирует имя типа marijari1999"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    year = random.randint(1950, 2005)
    style = random.choice(['', '.', '_'])
    if style:
        return f"{first}{style}{last}{year}".lower()
    return f"{first}{last}{year}".lower()

def generate_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def get_chromedriver_path():
    """Находит chromedriver в системе"""
    # Проверяем стандартные пути
    possible_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        os.path.expanduser("~") + "/.local/bin/chromedriver",
        "/snap/bin/chromedriver"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Пробуем найти через which
    try:
        result = subprocess.run(["which", "chromedriver"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

def human_like_typing(element, text):
    """Имитирует набор текста с задержками"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def human_like_mouse_move(driver, element):
    """Имитирует движение мыши к элементу"""
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    time.sleep(random.uniform(0.3, 0.8))

def check_cloudflare(driver):
    """Проверяет наличие Cloudflare и ждёт ручного решения"""
    page_source = driver.page_source.lower()
    current_url = driver.current_url.lower()
    
    cloudflare_indicators = [
        "cloudflare",
        "challenge",
        "checking your browser",
        "please wait",
        "just a moment"
    ]
    
    for indicator in cloudflare_indicators:
        if indicator in page_source or indicator in current_url:
            print("\n⚠️ Cloudflare обнаружена!")
            print("Решите капчу вручную в открытом браузере...")
            print("После решения страница обновится автоматически")
            input("Нажмите Enter ПОСЛЕ решения Cloudflare...")
            return True
    return False

def register_mail_ee():
    """Регистрирует один аккаунт"""
    
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    # Настройки Chrome
    options = Options()
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Путь к chromedriver
    driver_path = get_chromedriver_path()
    if not driver_path:
        print("[-] chromedriver не найден!")
        print("Установите: sudo apt install chromium-driver")
        return False
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 1. Открыть страницу
        print("[1] Открываю страницу...")
        driver.get("https://login.mail.ee/signup?go=portal")
        time.sleep(8)
        
        # 2. Проверка Cloudflare
        if check_cloudflare(driver):
            driver.refresh()
            time.sleep(5)
            if check_cloudflare(driver):
                print("[-] Cloudflare не пропускает, попробуйте позже")
                return False
        
        wait = WebDriverWait(driver, 30)
        
        # 3. Принять куки
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nõustun')]")))
            human_like_mouse_move(driver, cookie_btn)
            cookie_btn.click()
            print("[2] Приняты куки")
            time.sleep(DELAY_AFTER_CLICK)
        except:
            print("[2] Кнопка куки не найдена, продолжаем...")
        
        # 4. Имя пользователя
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        human_like_mouse_move(driver, username_field)
        username_field.clear()
        human_like_typing(username_field, username)
        print(f"[3] Введено имя: {username}")
        time.sleep(DELAY_STEP)
        
        # 5. Проверить доступность
        check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontrolli saadavust')]")))
        human_like_mouse_move(driver, check_btn)
        check_btn.click()
        print("[4] Нажата Kontrolli saadavust")
        time.sleep(DELAY_AFTER_CLICK)
        
        # Проверка, что имя свободно
        try:
            error = driver.find_element(By.XPATH, "//div[contains(text(), 'pole saadaval')]")
            if error.is_displayed():
                print("[-] Имя занято, пробуем другое...")
                return False
        except:
            pass
        
        # 6. Пароль
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        human_like_mouse_move(driver, password_field)
        password_field.clear()
        human_like_typing(password_field, password)
        print("[5] Пароль введён")
        time.sleep(DELAY_STEP)
        
        # 7. Галочки
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for i, cb in enumerate(checkboxes):
            if not cb.is_selected():
                human_like_mouse_move(driver, cb)
                cb.click()
                print(f"[6] Отмечена галочка {i+1}")
                time.sleep(2)
        
        # 8. Создать аккаунт
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Loo uus konto')]")))
        human_like_mouse_move(driver, create_btn)
        create_btn.click()
        print("[7] Нажата Loo uus konto")
        time.sleep(5)
        
        # 9. hCaptcha (ручное решение)
        print("\n" + "!" * 50)
        print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ В ОТКРЫТОМ БРАУЗЕРЕ")
        print("Если капча не появилась, возможно регистрация уже завершена")
        print("!" * 50)
        input("Нажмите Enter ПОСЛЕ решения капчи...")
        
        # 10. Сохранить аккаунт
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"[+] Успешно сохранён: {email}")
        return True
        
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return False
    finally:
        driver.quit()

def main():
    print("=" * 60)
    print("Mail.ee Account Generator (Python 3.12)")
    print("=" * 60)
    print("\n⚠️ ВНИМАНИЕ:")
    print("   - Cloudflare решается ВРУЧНУЮ")
    print("   - hCaptcha решается ВРУЧНУЮ")
    print("   - Между шагами задержка 5-7 секунд")
    print("=" * 60)
    
    # Проверка chromedriver
    if not get_chromedriver_path():
        print("\n❌ chromedriver не установлен!")
        print("Установите: sudo apt install chromium-driver")
        return
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    success = 0
    for i in range(count):
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_mail_ee():
            success += 1
            print(f"[+] Аккаунт {i+1} создан")
        else:
            print(f"[-] Аккаунт {i+1} не создан")
        
        if i < count - 1:
            print(f"\n[*] Ожидание 15 секунд...")
            time.sleep(15)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Создано: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    # Установка selenium если не установлен
    try:
        import selenium
    except ImportError:
        print("Устанавливаю selenium...")
        os.system("pip install selenium")
    
    main()
