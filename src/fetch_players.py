import requests
import json
import pandas as pd

cookies = "_adv_sid=fc3e9018-48f7-4135-9309-87c396ec50dc; _adv_uid=c1790bdb-dea7-4355-9d8e-e23e50cc6d76; AD_VERGE_SESSION_COOKIE_V1=9f13d7bc-4472-4fca-ae47-a6876d6f10ec; ssp_test=control; _gcl_au=1.1.1247041708.1781558251; _ga=GA1.1.1070685381.1781558251; _dlt=1; __gads=ID=d81aec2afbc02ce5:T=1781558254:RT=1781558254:S=ALNI_MYdZM9waUVaV0GKXWAjhitOtXgJYg; __gpi=UID=000013f7d434d954:T=1781558254:RT=1781558254:S=ALNI_MY3QL2LSETq2aFNB_fYrHQUpd3VuA; __eoi=ID=d7b16467ce0a95e5:T=1781558254:RT=1781558254:S=AA-AfjaTZEpOhBxp7K8EwQw0Fn7q; cto_bundle=4E3BM18lMkZzTHBxZlElMkJrM1JpTTZyWEh4RjhkWkt3bVJzU1hMTjVPeTZFaiUyQkRxdU5XbVMxWk1KaDM5NkxNaWc3SUczaXdtMVZsVHY2JTJCbWhSUDBnbXUwUTFremM2YU1ocFVSSG1RcWN0amRhV1ZsNWxYJTJGYlNNaEM4WFpUVDBLQnpMN3BQNlo1JTJGNHhwMU53S1FaekJMRFZyakdvS2clM0QlM0Q; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22d5f6d274-58cb-4905-a027-1582250b9aa5%5C%22%2C%5B1781558250%2C968000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol_6MhgTDsE-gnn-oMcWrtdNQ-hSpACK3ZNmrD3rEIH5NDLE9KN8XJVUlS3h3DC96rN-7bKfCUqz_7ipUOP5VyxDEgmBLWLqifY2lI6w1_QLO0JJwcOfcBOcMWyHkPUY-15P6r75FNoMvT8loCvE3KBqCgCgzw%3D%3D%22%5D%5D; _ga_HNQ9P9MGZR=GS2.1.s1781558251$o1$g1$t1781558441$j8$l0$h0"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookies
}

joueurs = []
page = 0

while True:
    url = f"https://www.sofascore.com/api/v1/fantasy/round/1026/players?page={page}&sortParam=form&sortOrder=DESC"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if "players" not in data:
        print(f"Erreur page {page}: {data}")
        break
    
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

df = pd.DataFrame(joueurs)
print(f"\nTotal joueurs: {len(df)}")
df.to_csv("data/raw/players_sofascore.csv", index=False)
print("Fichier sauvegardé.")