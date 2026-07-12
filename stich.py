import os
import glob
import cv2
import numpy as np
from datetime import datetime
import re

FOLDER_GOTOWE = "output"
PLIK_WYNIKOWY = "FINALNA_MAPA_360.png"

pliki = glob.glob(os.path.join(FOLDER_GOTOWE, "*.png"))
if not pliki:
    print(f"Brak plików w folderze '{FOLDER_GOTOWE}'!")
    exit()

# Sortujemy chronologicznie
pliki.sort()

out_w = 4000
out_h = 2000

master_map = np.zeros((out_h, out_w, 3), dtype=np.float32)
waga_map = np.zeros((out_h, out_w, 1), dtype=np.float32)

udane_pliki = 0
print(f"Rozpoczynam szycie (metoda potęgowa) z {len(pliki)} plików...")

for plik in pliki:
    nazwa = os.path.basename(plik)
    
    dopasowanie = re.search(r'\d{14}', nazwa)
    if not dopasowanie: continue
        
    znacznik = dopasowanie.group()
    try:
        czas = datetime.strptime(znacznik, "%Y%m%d%H%M%S")
    except Exception:
        continue
    
    img = cv2.imread(plik)
    if img is None: continue
    
    sekundy_od_polnocy = czas.hour * 3600 + czas.minute * 60 + czas.second
    obrot = 0.5 - (sekundy_od_polnocy / 86400.0)
    przesuniecie_x = int(obrot * out_w)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, maska = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # Obliczamy odległość od krawędzi (im bliżej środka zdjęcia, tym wyższa wartość)
    waga = cv2.distanceTransform(maska, cv2.DIST_L2, 5)
    
    # Normalizujemy wyniki do przedziału od 0.0 do 1.0
    cv2.normalize(waga, waga, 0, 1.0, cv2.NORM_MINMAX)
    
    # ==========================================
    # MAGIA: Potęgujemy wagę!
    # 1.0^6 = 1.0 (środek zostaje silny)
    # Ale 0.5^6 = 0.015 (wszystko poza środkiem drastycznie traci znaczenie)
    # ==========================================
    waga = waga ** 6 
    
    waga = np.expand_dims(waga, axis=2)
    
    przesuniety_img = np.roll(img, przesuniecie_x, axis=1)
    przesunieta_waga = np.roll(waga, przesuniecie_x, axis=1)
    
    master_map += przesuniety_img.astype(np.float32) * przesunieta_waga
    waga_map += przesunieta_waga
    
    udane_pliki += 1
    print(f"  -> Zszyto: {nazwa}")

if udane_pliki > 0:
    print("\nZlepianie i wyrównywanie...")
    waga_map[waga_map == 0] = 1 
    master_map = master_map / waga_map
    
    cv2.imwrite(PLIK_WYNIKOWY, master_map.astype(np.uint8))
    print(f"SUKCES! Gotowa mapa: {PLIK_WYNIKOWY}")