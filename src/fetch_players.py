import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurer Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Chrome invisible
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

joueurs = []
page = 0

while True:
    url = f"https://www.sofascore.com/api/v1/fantasy/round/1026/players?page={page}&sortParam=form&sortOrder=DESC"
    
    driver.get(url)
    time.sleep(2)
    
    body = driver.find_element("tag name", "body").text
    data = json.loads(body)
    
    print(f"Page {page} — {len(data['players'])} joueurs")
    
    for item in data["players"]:
        fp = item.get("fantasyPlayer", {})
        player = fp.get("player", {})
        team = item.get("team", {})
        
        joueurs.append({
            "name": player.get("name", ""),
            "short_name": player.get("shortName", ""),
            "position": fp.get("position", ""),
            "team": team.get("name", ""),
            "price": item.get("price", 0),
            "total_score": fp.get("totalScore", 0),
            "average_score": fp.get("averageScore", 0),
            "owned_percentage": fp.get("ownedPercentage", 0),
            "form": fp.get("form", 0)
        })
    
    if not data.get("hasNextPage", False):
        break
    
    page += 1

driver.quit()

df = pd.DataFrame(joueurs)
print(f"\nTotal joueurs: {len(df)}")
print(df.head())

df.to_csv("data/raw/players_sofascore.csv", index=False)
print("\nFichier sauvegardé.")