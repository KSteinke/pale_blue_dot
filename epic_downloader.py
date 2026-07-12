import os
import sys
import requests

def pobierz_zdjecia_epic(data_yyyy_mm_dd):
    rok, miesiac, dzien = data_yyyy_mm_dd.split('-')
    api_url = f"https://epic.gsfc.nasa.gov/api/natural/date/{data_yyyy_mm_dd}"
    print(f"--- ETAP 1: Pobieranie dla daty {data_yyyy_mm_dd} ---")
    
    try:
        # Dodany timeout: 15 sekund na odpowiedź od API
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Błąd: Serwer NASA nie odpowiedział w porę przy pobieraniu listy zdjęć (Timeout).")
        return
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas łączenia z API: {e}")
        return

    zdjecia = response.json()
    if not zdjecia:
        print(f"Brak zdjęć dla daty {data_yyyy_mm_dd}.")
        return
        
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
            # Dodany timeout: (10 sekund na połączenie, 60 sekund na odebranie danych)
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
    # Odbieranie daty od skryptu głównego
    wybrana_data = sys.argv[1] if len(sys.argv) > 1 else "2026-07-09"
    pobierz_zdjecia_epic(wybrana_data)