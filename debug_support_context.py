
import strategy
import database

print("--- Checking System Support Context ---")
try:
    context = strategy.get_system_support_context()
    print(context)
except Exception as e:
    print(f"Error: {e}")
print("---------------------------------------")
