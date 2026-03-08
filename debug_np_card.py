import database
import json

def inspect_np_card(name):
    print(f"--- Inspecting {name} ---")
    res = database.search_servants(name, limit=1)
    if not res:
        print("Not Found")
        return

    svt = res[0]
    data = json.loads(svt['json_data'])
    nps = data.get('noblePhantasms', [])
    for np in nps:
        card = np.get('card')
        print(f"NP Name: {np.get('name')}")
        print(f"Raw Card Value: '{card}'")
        print(f"Lower Card Value: '{card.lower() if card else 'None'}'")

if __name__ == "__main__":
    inspect_np_card("アルトリア")
    inspect_np_card("モルガン")
    inspect_np_card("オベロン")
