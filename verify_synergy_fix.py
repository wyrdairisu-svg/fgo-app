import strategy
import database
import re

# Mocking database search if needed, but we can use real one since we are on the same machine
# strategy.py imports 'database' which is local.

text = "花咲翁とフローラの相性について教えて"
print(f"Testing input: {text}")

# Call the function
try:
    context = strategy.extract_data_context(text)
    print("--- Context Result ---")
    print(context)
    
    # Validation
    if "花咲翁" in context and "フローレンス・ナイチンゲール" in context:
        print("\nSUCCESS: Both servants found!")
    else:
        print("\nFAILURE: Missing servants.")
        if "花咲翁" not in context: print("- Missing Hanasaka")
        if "フローレンス" not in context: print("- Missing Flora")

except Exception as e:
    print(f"Error: {e}")
