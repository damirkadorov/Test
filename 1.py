#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator
Правильный порядок: имя → hCaptcha → проверка имени
"""

import time
import random
import string
import os

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
# =====================================================

FIRST_NAMES = ["mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", "rain", "silja", "marten", "merle", "andres", "triin", "priit"]
LAST_NAMES = ["jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"]

def generate_username():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    year = random.randint(1950, 2005)
    return f"{first}{last}{year}".lower()

def generate_password():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=12))

def register():
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # 1. Открыть страницу (автообход Cloudflare)
        print("[1] Открытие страницы...")
        sb.uc_open_with_reconnect("https://login.mail.ee/signup?go=portal", 15)
        time.sleep(3)
        
        # 2. Принять куки
        print("[2] Принятие куки...")
        try:
            sb.click("#accept-btn", timeout=5)
            print("[✓] Куки приняты")
        except:
            print("[!] Куки не найдены")
        time.sleep(2)
        
        # 3. Ввод имени (kasutajanimi)
        print("[3] Ввод имени...")
        sb.type("#signup_user", username)
        print(f"[✓] Имя: {username}")
        time.sleep(2)
        
        # 4. hCaptcha (на этом этапе появляется капча!)
        print("\n" + "!" * 50)
        print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ (капча после ввода имени)")
        print("!" * 50)
        input("Нажмите Enter ПОСЛЕ решения капчи...")
        
        # 5. Проверка имени (Kontrolli saadavust) - только после капчи!
        print("[4] Проверка доступности имени...")
        sb.click("#check-uname")
        time.sleep(3)
        
        # 6. Ввод пароля
        print("[5] Ввод пароля...")
        sb.type("input[name='password']", password)
        print("[✓] Пароль введён")
        time.sleep(2)
        
        # 7. Отметка галочек
        print("[6] Отметка галочек...")
        for cb in sb.find_elements("//input[@type='checkbox']"):
            if not cb.is_selected():
                cb.click()
                time.sleep(1)
        
        # 8. Создание аккаунта
        print("[7] Создание аккаунта...")
        sb.click("//button[contains(text(), 'Loo uus konto')]")
        time.sleep(3)
        
        # 9. Сохранение
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"[+] Аккаунт сохранён: {email}")
        return True

def main():
    print("=" * 60)
    print("Mail.ee Account Generator")
    print("Правильный порядок: имя → hCaptcha → проверка имени")
    print("=" * 60)
    
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    
    print("\n⚠️ ПОРЯДОК ДЕЙСТВИЙ:")
    print("   1. Cloudflare обходится автоматически")
    print("   2. Куки принимаются автоматически")
    print("   3. Вводится имя (kasutajanimi)")
    print("   4. 🔐 ВЫ РЕШАЕТЕ hCaptcha ВРУЧНУЮ")
    print("   5. Автоматически нажимается проверка имени")
    print("   6. Вводится пароль, галочки, создание")
    print("   7. Аккаунт сохраняется")
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
        
        if register():
            success += 1
        else:
            print(f"[-] Ошибка")
        
        if i < count - 1:
            print("\n[*] Ожидание 10 секунд...")
            time.sleep(10)
    
    print("\n" + "=" * 60)
    print(f"✅ Создано: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
