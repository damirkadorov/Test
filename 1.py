#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT Registration Bot
Универсальный поиск полей по HTML (лейблы, placeholder)
"""

import time
import random
import string
import os
import imaplib
import email
import re

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
EMAILS_FILE = "emails.txt"
OUTPUT_FILE = "chatgpt_accounts.txt"
DELAY_STEP = 3
FIXED_PASSWORD = "Mudakiv12345@"

# IMAP для Firstmail
FIRSTMAIL_IMAP = "imap.firstmail.ltd"
FIRSTMAIL_IMAP_PORT = 993
# =====================================================

def human_type(element, text, delay_min=0.05, delay_max=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(delay_min, delay_max))

def get_verification_code(email, password, timeout=120):
    try:
        mail = imaplib.IMAP4_SSL(FIRSTMAIL_IMAP, FIRSTMAIL_IMAP_PORT)
        mail.login(email, password)
        mail.select('inbox')
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            print(f"[*] Проверка писем...")
            result, data = mail.search(None, '(FROM "openai.com" OR FROM "tm.openai.com")')
            
            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                if email_ids:
                    latest_id = email_ids[-1]
                    result, msg_data = mail.fetch(latest_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                body = payload.decode('utf-8', errors='ignore')
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        body = payload.decode('utf-8', errors='ignore')
                    
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        code = match.group(1)
                        print(f"[+] Код: {code}")
                        mail.close()
                        mail.logout()
                        return code
            
            time.sleep(5)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"[!] Ошибка IMAP: {e}")
    
    return None

def find_field_by_label(sb, label_text, timeout=5):
    """Ищет поле ввода по тексту лейбла"""
    try:
        # Ищем лейбл с текстом
        xpath = f"//label[contains(text(), '{label_text}')]"
        label = sb.find_element(xpath, timeout=timeout)
        if label:
            # Ищем связанный input
            for_id = label.get_attribute("for")
            if for_id:
                try:
                    field = sb.find_element(f"#{for_id}", timeout=2)
                    if field:
                        return field
                except:
                    pass
            
            # Ищем input рядом с лейблом
            try:
                field = sb.find_element(f"{xpath}/following-sibling::input", timeout=2)
                if field:
                    return field
            except:
                pass
            
            # Ищем input внутри родителя
            try:
                field = sb.find_element(f"{xpath}/ancestor::div//input", timeout=2)
                if field:
                    return field
            except:
                pass
    except:
        pass
    return None

def find_field_by_placeholder(sb, placeholder_text, timeout=5):
    """Ищет поле ввода по placeholder"""
    try:
        field = sb.find_element(f"input[placeholder*='{placeholder_text}']", timeout=timeout)
        if field:
            return field
    except:
        pass
    return None

def find_field_by_type(sb, input_type, timeout=5):
    """Ищет поле ввода по типу"""
    try:
        field = sb.find_element(f"input[type='{input_type}']", timeout=timeout)
        if field:
            return field
    except:
        pass
    return None

def find_password_field(sb, timeout=10):
    """Ищет поле пароля разными способами"""
    
    # Способ 1: по лейблу "Password"
    field = find_field_by_label(sb, "Password", timeout)
    if field:
        print("[✓] Поле пароля найдено по лейблу 'Password'")
        return field
    
    # Способ 2: по лейблу "Пароль"
    field = find_field_by_label(sb, "Пароль", timeout)
    if field:
        print("[✓] Поле пароля найдено по лейблу 'Пароль'")
        return field
    
    # Способ 3: по placeholder "Password"
    field = find_field_by_placeholder(sb, "Password", timeout)
    if field:
        print("[✓] Поле пароля найдено по placeholder 'Password'")
        return field
    
    # Способ 4: по типу password
    field = find_field_by_type(sb, "password", timeout)
    if field:
        print("[✓] Поле пароля найдено по type='password'")
        return field
    
    # Способ 5: по атрибуту name содержащему password
    try:
        field = sb.find_element("input[name*='password']", timeout=timeout)
        if field:
            print("[✓] Поле пароля найдено по name*='password'")
            return field
    except:
        pass
    
    print("[-] Поле пароля не найдено")
    return None

def find_name_field(sb, timeout=5):
    """Ищет поле имени"""
    for label in ["First name", "Name", "Имя", "Full name"]:
        field = find_field_by_label(sb, label, timeout)
        if field:
            return field
    
    for placeholder in ["Name", "First name", "Имя"]:
        field = find_field_by_placeholder(sb, placeholder, timeout)
        if field:
            return field
    
    try:
        field = sb.find_element("input[name='first_name']", timeout=timeout)
        if field:
            return field
    except:
        pass
    
    return None

def find_date_field(sb, timeout=5):
    """Ищет поле даты рождения"""
    for label in ["Birth date", "Date of birth", "Дата рождения"]:
        field = find_field_by_label(sb, label, timeout)
        if field:
            return field
    
    try:
        field = sb.find_element("input[type='date']", timeout=timeout)
        if field:
            return field
    except:
        pass
    
    return None

def register_chatgpt(email, email_password):
    chatgpt_password = FIXED_PASSWORD
    
    print(f"\n{'='*50}")
    print(f"[*] Почта: {email}")
    print(f"[*] Пароль ChatGPT: {chatgpt_password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # 1. Открытие
        print("\n[1] Открытие ChatGPT...")
        sb.uc_open_with_reconnect("https://chatgpt.com", 20)
        time.sleep(DELAY_STEP)
        
        # 2. Sign up
        print("\n[2] Нажатие Sign up...")
        try:
            sb.click("button[data-testid='signup-button']", timeout=10)
        except:
            sb.click("//button[contains(text(), 'Sign up')]", timeout=10)
        time.sleep(DELAY_STEP)
        
        # 3. Email
        print("\n[3] Ввод email...")
        email_field = find_field_by_type(sb, "email", 10)
        if not email_field:
            email_field = find_field_by_label(sb, "Email", 10)
        if email_field:
            human_type(email_field, email)
            print(f"[✓] Email: {email}")
        else:
            print("[-] Поле email не найдено")
            return False
        time.sleep(DELAY_STEP)
        
        # 4. Continue после email
        print("\n[4] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 5. Пароль
        print("\n[5] Поиск поля пароля...")
        password_field = find_password_field(sb, timeout=10)
        if not password_field:
            print("[-] Поле пароля не найдено")
            return False
        
        human_type(password_field, chatgpt_password)
        print(f"[✓] Пароль: {chatgpt_password}")
        time.sleep(DELAY_STEP)
        
        # 6. Continue после пароля
        print("\n[6] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 7. Ожидание кода
        print("\n[7] Ожидание кода...")
        try:
            sb.wait_for_element_visible("input[name='code']", timeout=30)
            print("[✓] Поле кода появилось")
        except:
            print("[-] Поле кода не появилось")
            return False
        
        # 8. Получение кода
        print("\n[8] Получение кода...")
        code = get_verification_code(email, email_password, timeout=120)
        if not code:
            return False
        
        # 9. Ввод кода
        print(f"\n[9] Ввод кода: {code}")
        code_field = sb.find_element("input[name='code']")
        human_type(code_field, code)
        time.sleep(DELAY_STEP)
        
        # 10. Continue после кода
        print("\n[10] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 11. Имя
        print("\n[11] Поиск поля имени...")
        name_field = find_name_field(sb, timeout=5)
        if name_field:
            human_type(name_field, "John Smith")
            print("[✓] Имя: John Smith")
            time.sleep(DELAY_STEP)
            try:
                sb.click("button[type='submit']")
                print("[✓] Continue после имени")
                time.sleep(DELAY_STEP)
            except:
                pass
        else:
            print("[!] Поле имени не найдено")
        
        # 12. Дата рождения
        print("\n[12] Поиск поля даты...")
        date_field = find_date_field(sb, timeout=5)
        if date_field:
            human_type(date_field, "2000-01-01")
            print("[✓] Дата: 2000-01-01")
            time.sleep(DELAY_STEP)
            try:
                sb.click("button[type='submit']")
                print("[✓] Continue после даты")
                time.sleep(DELAY_STEP)
            except:
                pass
        else:
            print("[!] Поле даты не найдено")
        
        # Сохранение
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{chatgpt_password}\n")
        
        print(f"\n[+] Аккаунт сохранён: {email}")
        return True

def load_emails():
    emails = []
    try:
        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    email, pwd = line.split(':', 1)
                    emails.append((email, pwd))
        print(f"[+] Загружено {len(emails)} аккаунтов")
    except FileNotFoundError:
        print(f"[-] Файл {EMAILS_FILE} не найден!")
    return emails

def main():
    print("=" * 60)
    print("ChatGPT Registration Bot")
    print("Универсальный поиск полей (по лейблам, placeholder, типу)")
    print("=" * 60)
    
    emails = load_emails()
    if not emails:
        return
    
    count = int(input("\nСколько аккаунтов создать: ") or len(emails))
    count = min(count, len(emails))
    
    success = 0
    for i in range(count):
        email, email_password = emails[i]
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_chatgpt(email, email_password):
            success += 1
        else:
            print(f"[-] Ошибка")
        
        if i < count - 1:
            print("\n[*] Ожидание 10 сек...")
            time.sleep(10)
    
    print(f"\n✅ Готово: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
