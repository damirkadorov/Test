#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator с SeleniumBase
Автоматический обход Cloudflare и ручное решение hCaptcha
"""

import time
import random
import string

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
DELAY_STEP = 5
DELAY_AFTER_CLICK = 7
# =====================================================

# Реалистичные имена
FIRST_NAMES = ["mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", "rain", "silja", "marten", "merle", "andres", "triin", "priit"]
LAST_NAMES = ["jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"]

def generate_username():
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

def register_mail_ee():
    """Регистрирует один аккаунт с использованием SeleniumBase"""
    
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    # Используем SeleniumBase с UC Mode для обхода Cloudflare
    # uc=True включает Undetected Mode
    # ad_block_on=True блокирует рекламу для ускорения
    with SB(uc=True, ad_block_on=True, incognito=True) as sb:
        
        # 1. Открыть страницу с автоматическим обходом Cloudflare
        print("\n--- ЭТАП 1: Открытие страницы (обход Cloudflare) ---")
        sb.uc_open_with_reconnect("https://login.mail.ee/signup?go=portal", 15)
        print("[✓] Cloudflare обойдена (если была)")
        time.sleep(5)
        
        # 2. Принять куки (кнопка "Nõustun")
        print("\n--- ЭТАП 2: Принятие куки ---")
        try:
            sb.click("//button[contains(text(), 'Nõustun')]", timeout=10)
            print("[✓] Куки приняты")
            time.sleep(DELAY_AFTER_CLICK)
        except:
            print("[!] Кнопка куки не найдена")
        
        # 3. Ввод имени пользователя
        print("\n--- ЭТАП 3: Ввод имени пользователя ---")
        sb.type("input[name='username']", username, timeout=10)
        print(f"[✓] Имя введено: {username}")
        time.sleep(DELAY_STEP)
        
        # 4. Проверка доступности имени
        print("\n--- ЭТАП 4: Проверка доступности имени ---")
        sb.click("//button[contains(text(), 'Kontrolli saadavust')]")
        print("[✓] Нажата Kontrolli saadavust")
        time.sleep(DELAY_AFTER_CLICK)
        
        # Проверяем, свободно ли имя
        if sb.is_text_visible("pole saadaval"):
            print("[-] Имя занято, пробуем другое...")
            return False
        
        # 5. Ввод пароля
        print("\n--- ЭТАП 5: Ввод пароля ---")
        sb.type("input[name='password']", password)
        print("[✓] Пароль введён")
        time.sleep(DELAY_STEP)
        
        # 6. Отметка галочек
        print("\n--- ЭТАП 6: Отметка галочек ---")
        checkboxes = sb.find_elements("//input[@type='checkbox']")
        for i, cb in enumerate(checkboxes):
            if not cb.is_selected():
                sb.click(cb)
                print(f"[✓] Галочка {i+1} отмечена")
                time.sleep(2)
        
        # 7. Создание аккаунта
        print("\n--- ЭТАП 7: Создание аккаунта ---")
        sb.click("//button[contains(text(), 'Loo uus konto')]")
        print("[✓] Нажата Loo uus konto")
        time.sleep(5)
        
        # 8. Обработка hCaptcha (автоматический клик на чекбокс)
        print("\n--- ЭТАП 8: Обработка hCaptcha ---")
        try:
            # Пробуем автоматически кликнуть на чекбокс капчи
            sb.uc_gui_click_captcha(timeout=10)
            print("[✓] hCaptcha чекбокс нажат автоматически")
        except:
            print("[!] Автоматический клик не сработал, нужна ручная помощь")
        
        # Ждём ручного решения, если капча всё ещё есть
        if sb.is_element_present("iframe[src*='captcha']", timeout=5):
            print("\n" + "!" * 50)
            print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ В ОТКРЫТОМ БРАУЗЕРЕ")
            print("!" * 50)
            input("Нажмите Enter ПОСЛЕ решения капчи...")
        
        # 9. Сохранение аккаунта
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"\n[+] Успешно сохранён: {email}")
        return True

def main():
    print("=" * 60)
    print("Mail.ee Account Generator с SeleniumBase")
    print("Автоматический обход Cloudflare")
    print("=" * 60)
    print("\n⚠️ ВНИМАНИЕ:")
    print("   - Cloudflare обходится АВТОМАТИЧЕСКИ (UC Mode)")
    print("   - hCaptcha требует РУЧНОГО решения (иногда автоматический клик)")
    print("   - Между шагами задержка 5-7 секунд")
    print("=" * 60)
    
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
        else:
            print(f"[-] Аккаунт {i+1} не создан")
        
        if i < count - 1:
            print(f"\n[*] Ожидание 20 секунд...")
            time.sleep(20)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Создано: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
