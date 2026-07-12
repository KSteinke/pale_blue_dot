import os
import sys
import glob
import numpy as np
import cv2

def rozciagnij_na_prostokat(sciezka_wejsciowa, folder_gotowe):
    nazwa_pliku = os.path.basename(sciezka_wejsciowa)
    sciezka_wyjsciowa = os.path.join(folder_gotowe, f"mapa_{nazwa_pliku}")

    img = cv2.imread(sciezka_wejsciowa)
    if img is None:
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours: return
        
    c = max(contours, key=cv2.contourArea)
    ((cx, cy), promien_ziemi) = cv2.minEnclosingCircle(c)
    promien_ziemi = promien_ziemi * 0.99 
    
    out_w, out_h = 4000, 2000
    U, V = np.meshgrid(np.linspace(0, 1, out_w), np.linspace(0, 1, out_h))
    
    lon = (U - 0.5) * 2 * np.pi
    lat = (0.5 - V) * np.pi 
    
    X = np.cos(lat) * np.sin(lon)
    Y = np.sin(lat)
    Z = np.cos(lat) * np.cos(lon)
    
    img_x = (X * promien_ziemi) + cx
    img_y = (-Y * promien_ziemi) + cy 
    
    img_x[Z < 0] = -1
    img_y[Z < 0] = -1
    
    unwrapped = cv2.remap(img, img_x.astype(np.float32), img_y.astype(np.float32), 
                          cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    
    margines = int(out_h * 0.08)
    unwrapped_cropped = unwrapped[margines : out_h - margines, :]
    unwrapped_clean = cv2.resize(unwrapped_cropped, (out_w, out_h), interpolation=cv2.INTER_CUBIC)
    
    cv2.imwrite(sciezka_wyjsciowa, unwrapped_clean)
    print(f"  -> Zapisano: {sciezka_wyjsciowa} (Promień: {int(promien_ziemi)}px)")

if __name__ == "__main__":
    wybrana_data = sys.argv[1] if len(sys.argv) > 1 else "2026-07-09"
    print(f"--- ETAP 2: Transformacja zdjęć dla daty {wybrana_data} ---")
    
    folder_wejsciowe = f"download\\{wybrana_data}"
    folder_gotowe = f"output\\{wybrana_data}"
    
    os.makedirs(folder_gotowe, exist_ok=True)
    pliki_png = glob.glob(os.path.join(folder_wejsciowe, "*.png"))

    if not pliki_png:
        print(f"Brak plików w folderze {folder_wejsciowe}.")
    else:
        for plik in pliki_png:
            rozciagnij_na_prostokat(plik, folder_gotowe)
        print("\n")