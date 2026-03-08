import db_builder
import database
import os
import shutil

# Clean up before test (optional, but good for verification)
# if os.path.exists("cache"):
#     shutil.rmtree("cache")

print("=== Running Update ===")
logs = db_builder.run_update()
print("Logs:", logs)

print("\n=== Checking Cache ===")
if os.path.exists("cache"):
    print("Cache directory exists.")
    files = os.listdir("cache")
    print("Cache files:", files)
else:
    print("Cache directory MISSING.")

print("\n=== Checking Last Updated Time ===")
last_updated = database.get_last_updated_time()
print("Last Updated:", last_updated)
