import os
import sys
import socket
import requests
import requests.packages.urllib3.util.connection as urllib3_cn

def allowed_gai_family():
    return socket.AF_INET # Wymusza IPv4



def pobierz_zdjecia_epic(data_yyyy_mm_dd):
    rok, miesiac, dzien = data_yyyy_mm_dd.split('-')
    url = f"https://epic.gsfc.nasa.gov/api/natural/date/{data_yyyy_mm_dd}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    print(f"--- ETAP 1: Pobieranie dla daty {data_yyyy_mm_dd} ---")
    
    # KROK 1: Inicjalizacja zmiennej na start. 
    # Dzięki temu Python NIGDY więcej nie powie, że zmienna nie istnieje.
    zdjecia = None
    
    try:
        print(f"Próbuję połączyć z: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() 
        
        # Jeśli połączenie się udało, przypisujemy dane
        zdjecia = response.json()
        print("Sukces! Pobrano listę zdjęć.")
    
    except requests.exceptions.Timeout:
        print("BŁĄD: Prawdziwy Timeout. Serwer NASA milczy od 30 sekund.")
    except requests.exceptions.HTTPError as err:
        print(f"BŁĄD HTTP: Serwer odpowiedział statusem błędu: {err}")
    except Exception as e:
        print(f"INNY BŁĄD: {e}")

    # KROK 2: Jedno główne miejsce weryfikacji.
    # Jeśli wystąpił błąd wyżej (zdjecia to nadal None) LUB NASA zwróciła pustą listę []
    if not zdjecia:
        print(f"[STOP] Nie można kontynuować procesu dla daty {data_yyyy_mm_dd} z powodu braku danych.")
        sys.exit(1) # Zatrzymujemy skrypt i dajemy jasny sygnał do process.py
        
    nazwa_folderu = f"download\\{data_yyyy_mm_dd}"
    os.makedirs(nazwa_folderu, exist_ok=True)
    
    for index, element in enumerate(zdjecia, start=1):
        nazwa_pliku = element['image'] + ".png"
        url_zdjecia = f"https://epic.gsfc.nasa.gov/archive/natural/{rok}/{miesiac}/{dzien}/png/{nazwa_pliku}"
        sciezka_do_zapisu = os.path.join(nazwa_folderu, nazwa_pliku)
        
        if os.path.exists(sciezka_do_zapisu):
            print(f"[{index}/{len(zdjecia)}] Plik {nazwa_pliku} już istnieje, pomijam.")
            continue
            
        print(f"[{index}/{len(zdjecia)}] Pobieranie {nazwa_pliku} ...")
        try:
            img_response = requests.get(url_zdjecia, stream=True, timeout=(10, 60))
            img_response.raise_for_status()
            
            with open(sciezka_do_zapisu, 'wb') as f:
                for chunk in img_response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        except requests.exceptions.Timeout:
            print(f"  -> [INFO] Timeout! Serwer NASA przestał wysyłać dane dla pliku {nazwa_pliku}.")
        except requests.exceptions.RequestException as e:
            print(f"  -> Błąd podczas pobierania {nazwa_pliku}: {e}")

    print(f"Zakończono pobieranie do folderu: {nazwa_folderu}\n")

if __name__ == "__main__":
    urllib3_cn.allowed_gai_family = allowed_gai_family
    wybrana_data = sys.argv[1] if len(sys.argv) > 1 else "2026-07-09"
    pobierz_zdjecia_epic(wybrana_data)