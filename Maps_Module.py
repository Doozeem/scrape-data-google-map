from playwright.sync_api import sync_playwright
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

def clean_url(raw_url):
    """Membongkar jebakan redirect Google untuk mendapatkan URL asli"""
    if "url?q=" in raw_url:
        parsed = urlparse(raw_url)
        return parse_qs(parsed.query).get('q', [raw_url])[0]
    return raw_url

def find_emails_on_website(page, raw_website_url):
    """Infiltrasi Mendalam: Mencari email melalui teks dan link mailto secara sinkron"""
    website_url = clean_url(raw_website_url)
    
    # Lewati pencarian jika target hanya berupa media sosial
    if website_url == "N/A" or "instagram.com" in website_url or "facebook.com" in website_url:
        return "Social Media Only"
    
    try:
        print(f"  [DEEP SCAN] Menginfiltrasi: {website_url}")
        # Masuk ke website target dengan batas waktu 15 detik
        page.goto(website_url, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000) # Jeda untuk membiarkan script target merender teks

        content = page.content()
        
        # Teknik 1: Regex pada konten teks (Mencari pola email standar)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        
        # Teknik 2: Mencari atribut mailto (Membongkar tombol "Contact Us")
        mailto_links = page.query_selector_all('a[href^="mailto:"]')
        for link in mailto_links:
            href = link.get_attribute('href')
            if href:
                email_from_href = href.replace('mailto:', '').split('?')[0]
                emails.append(email_from_href)

        # Pembersihan duplikat dan file gambar yang terdeteksi sebagai email
        unique_emails = list(set([e.lower() for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]))
        return ", ".join(unique_emails) if unique_emails else "No Email Visible"
    except Exception:
        return "Protected/Timeout"

def scrape_google_maps(target_keyword, total_leads=10):
    """Mesin Utama Infiltrasi v3.1 (Sync Engine)"""
    print(f"[ORION] Memulai pemindaian target: {target_keyword} (Mode Sinkron)")
    
    with sync_playwright() as p:
        # Menjalankan Chromium dalam bayangan (Headless) agar tidak mengganggu Dashboard
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        email_page = context.new_page() # Tab sekunder khusus untuk Deep Scan

        search_url = f"https://www.google.com/maps/search/{target_keyword.replace(' ', '+')}"
        page.goto(search_url)

        # Hancurkan Barikade Persetujuan Cookie
        try:
            page.click('button[aria-label*="Accept"], button[aria-label*="Terima"]', timeout=5000)
        except: 
            pass # Jika tidak ada dialog, lanjutkan operasi

        leads = []
        while len(leads) < total_leads:
            try:
                page.wait_for_selector('a.hfpxzc', timeout=15000)
            except:
                print("[!] Target tidak ditemukan atau Google memblokir radar. Operasi dihentikan.")
                break

            links = page.query_selector_all('a.hfpxzc')
            
            for link in links:
                if len(leads) >= total_leads: break
                
                try:
                    name = link.get_attribute('aria-label')
                    # Cegah pengambilan data duplikat
                    if not name or any(l.get('Nama') == name for l in leads): 
                        continue

                    # Eksekusi klik simulasi manusia
                    link.click()
                    page.wait_for_timeout(2500)

                    # Ekstraksi Detail Bisnis
                    phone_el = page.query_selector('button[data-item-id*="phone:tel"]')
                    phone = phone_el.inner_text() if phone_el else "N/A"
                    
                    website_el = page.query_selector('a[data-item-id="authority"]')
                    website = website_el.get_attribute('href') if website_el else "N/A"
                    
                    cat_el = page.query_selector('button[jsaction*="category"]')
                    category = cat_el.inner_text() if cat_el else "Business"

                    # Pemurnian Data Telepon (Menghapus simbol aneh seperti )
                    phone = re.sub(r'[^\x00-\x7F]+', '', phone).strip()

                    # Luncurkan Tab Sekunder untuk Deep Scan Email
                    email = "N/A"
                    if website != "N/A":
                        email = find_emails_on_website(email_page, website)

                    leads.append({
                        "Nama": name,
                        "Kategori": category,
                        "Telepon": phone,
                        "Email": email,
                        "Website": clean_url(website)
                    })
                    print(f"[JARAHAN] {name} | Email: {email}")

                except Exception: 
                    continue

            # Manuver Scroll untuk memaksa Google Maps memuat data baru
            page.mouse.move(200, 400)
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(3000)

        # Menutup browser dan mengirimkan jarahan ke Dashboard
        browser.close()
        return pd.DataFrame(leads)