import os
import glob
import numpy as np
import cv2

FOLDER_WEJSCIOWE = "download" 
FOLDER_GOTOWE = "output"

def przygotuj_foldery():
    if not os.path.exists(FOLDER_WEJSCIOWE): os.makedirs(FOLDER_WEJSCIOWE)
    if not os.path.exists(FOLDER_GOTOWE): os.makedirs(FOLDER_GOTOWE)

def rozciagnij_na_prostokat(sciezka_wejsciowa):
    nazwa_pliku = os.path.basename(sciezka_wejsciowa)
    sciezka_wyjsciowa = os.path.join(FOLDER_GOTOWE, f"mapa_{nazwa_pliku}")

    img = cv2.imread(sciezka_wejsciowa)
    if img is None:
        print(f"  [BŁĄD] Nie można wczytać pliku {sciezka_wejsciowa}.")
        return

    # --- NOWA, INTELIGENTNA CZĘŚĆ (Auto-detekcja Ziemi) ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Odcinamy czarny kosmos (wszystko jaśniejsze niż 5/255 to Ziemia)
    _, thresh = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)
    
    # Szukamy konturów jasnego obiektu
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"  [BŁĄD] Nie znalazłem Ziemi na zdjęciu {nazwa_pliku} (jest całe czarne?).")
        return
        
    # Wybieramy największy znaleziony obiekt (naszą planetę)
    c = max(contours, key=cv2.contourArea)
    
    # Obliczamy idealny środek (cx, cy) i promień Ziemi co do piksela
    ((cx, cy), promien_ziemi) = cv2.minEnclosingCircle(c)
    
    # Zmniejszamy promień o symboliczny 1%, aby uciąć ciemną poświatę atmosfery na brzegach
    promien_ziemi = promien_ziemi * 0.99 
    # -----------------------------------------------------
    
    out_w = 4000
    out_h = 2000
    
    U, V = np.meshgrid(np.linspace(0, 1, out_w), np.linspace(0, 1, out_h))
    
    lon = (U - 0.5) * 2 * np.pi
    lat = (0.5 - V) * np.pi 
    
    X = np.cos(lat) * np.sin(lon)
    Y = np.sin(lat)
    Z = np.cos(lat) * np.cos(lon)
    
    # Używamy teraz dokładnie wykrytego środka i promienia (koniec ze zgadywaniem)
    img_x = (X * promien_ziemi) + cx
    img_y = (-Y * promien_ziemi) + cy 
    
    img_x[Z < 0] = -1
    img_y[Z < 0] = -1
    
    # Rozciąganie
    unwrapped = cv2.remap(img, img_x.astype(np.float32), img_y.astype(np.float32), 
                          cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    
    cv2.imwrite(sciezka_wyjsciowa, unwrapped)
    print(f"  -> Zapisano: {sciezka_wyjsciowa} (Wykryty promień: {int(promien_ziemi)}px)")

# ================= GŁÓWNY PROGRAM =================
przygotuj_foldery()
pliki_png = glob.glob(os.path.join(FOLDER_WEJSCIOWE, "*.png"))

if not pliki_png:
    print("Brak plików w folderze wejściowym.")
else:
    for plik in pliki_png:
        print(f"Przetwarzanie {os.path.basename(plik)}...")
        rozciagnij_na_prostokat(plik)