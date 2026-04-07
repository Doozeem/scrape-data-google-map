from playwright.sync_api import sync_playwright
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

def clean_url(raw_url):
    if "url?q=" in raw_url:
        parsed = urlparse(raw_url)
        return parse_qs(parsed.query).get('q', [raw_url])[0]
    return raw_url

def find_emails_on_website(page, raw_website_url):
    website_url = clean_url(raw_website_url)
    if website_url == "N/A" or "instagram.com" in website_url or "facebook.com" in website_url:
        return "Social Media Only"
    
    try:
        page.goto(website_url, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        content = page.content()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        unique_emails = list(set([e.lower() for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif'))]))
        return ", ".join(unique_emails) if unique_emails else "No Email Visible"
    except Exception:
        return "Protected/Timeout"

def scrape_google_maps(target_keyword, total_leads=10):
    with sync_playwright() as p:
        # Argumen khusus agar Playwright bisa berjalan di Server Cloud Linux
        browser = p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        email_page = context.new_page()

        search_url = f"https://www.google.com/maps/search/{target_keyword.replace(' ', '+')}"
        
        try:
            page.goto(search_url, timeout=60000)
            try: page.click('button[aria-label*="Accept"], button[aria-label*="Terima"]', timeout=3000)
            except: pass
                
            leads = []
            while len(leads) < total_leads:
                try: page.wait_for_selector('a.hfpxzc', timeout=15000)
                except: break

                links = page.query_selector_all('a.hfpxzc')
                
                for link in links:
                    if len(leads) >= total_leads: break
                    try:
                        name = link.get_attribute('aria-label')
                        if not name or any(l.get('Nama') == name for l in leads): continue

                        link.click()
                        page.wait_for_timeout(2500)

                        phone_el = page.query_selector('button[data-item-id*="phone:tel"]')
                        phone = phone_el.inner_text() if phone_el else "N/A"
                        website_el = page.query_selector('a[data-item-id="authority"]')
                        website = website_el.get_attribute('href') if website_el else "N/A"
                        cat_el = page.query_selector('button[jsaction*="category"]')
                        category = cat_el.inner_text() if cat_el else "Business"

                        phone = re.sub(r'[^\x00-\x7F]+', '', phone).strip()
                        email = find_emails_on_website(email_page, website) if website != "N/A" else "N/A"

                        leads.append({
                            "Nama": name, "Kategori": category, "Telepon": phone, 
                            "Email": email, "Website": clean_url(website)
                        })
                    except Exception: 
                        continue

                page.mouse.move(200, 400)
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(3000)

        except Exception as e:
            print(f"Error navigasi: {e}")
        finally:
            browser.close()
            
        return pd.DataFrame(leads)
