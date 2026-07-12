import subprocess
import sys

# Ustaw datę, którą chcesz przetworzyć
wybrana_data = "2026-07-05"

skrypty = ["epic_downloader.py", "epic_skaner.py", "stich.py"]

print("="*50)
print(f"ROZPOCZYNAM AUTOMATYCZNY PROCES DLA DATY: {wybrana_data}")
print("="*50)

for skrypt in skrypty:
    try:
        # sys.executable to ścieżka do Twojego Pythona (z venv)
        # Przekazujemy wybraną datę jako dodatkowy argument do każdego skryptu
        subprocess.run([sys.executable, skrypt, wybrana_data], check=True)
    except subprocess.CalledProcessError:
        print(f"\n[BŁĄD KRYTYCZNY] Skrypt {skrypt} napotkał problem.")
        print("Zatrzymuję całą kolejkę, aby nie generować błędnych plików.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n[BŁĄD] Nie znaleziono pliku: {skrypt}. Upewnij się, że jesteś w dobrym folderze.")
        sys.exit(1)

print("="*50)
print("WSZYSTKIE PROCESY ZAKOŃCZONE POMYŚLNIE!")
print(f"Finalny globus czeka w folderze assets\\{wybrana_data}.png")
print("="*50)