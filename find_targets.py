import database
import json

def search(query):
    print(f"--- Searching for {query} ---")
    results = database.search_servants(query=query)
    for r in results:
        print(f"ID: {r['id']}, Name: {r['name']}, Class: {r['class_name']}")

search("オルガマリー")
search("エレシュキガル")
