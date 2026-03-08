import database

print("--- CE ---")
ces = database.search_craft_essences(limit=1)
if ces:
    print(ces[0])
else:
    print("No CEs found")

print("\n--- CC ---")
ccs = database.search_command_codes(limit=1)
if ccs:
    print(ccs[0])
else:
    print("No CCs found")

print("\n--- Items ---")
items = database.search_materials(limit=1)
if items:
    print(items[0])
else:
    print("No Items found")
