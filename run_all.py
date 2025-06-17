import os
import subprocess
from datetime import datetime

print("\n🚀 Käynnistetään koko analyysiputki...")

# 1. Generoi uusin opetusdata (valinnainen - voi kommentoida jos ei haluta ajaa joka kerta)
print("\n📦 Luodaan opetusaineisto...")
os.system("python generate_training_data.py")

# 2. Kouluta malli uusimmalla datalla
print("\n🧠 Koulutetaan malli...")
os.system("python train_model.py")

# 3. Päivitä tietokanta ja tarkista signaalit
print("\n🔍 Skannataan markkina...")
os.system("python scan_market.py")

# 4. Tulosta yhteenveto
print("\n✅ Valmis!")
print(f"Päiväys: {datetime.today().strftime('%Y-%m-%d')}")
print("Signaalit löytyvät tietokannasta (signals.db) ja dashboardista (signal_dashboard.py)")
