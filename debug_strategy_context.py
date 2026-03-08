
import strategy
import database

def debug_context(query):
    print(f"--- Query: {query} ---")
    context = strategy.extract_data_context(query)
    print(context)
    print("----------------------\n")

# Test with the problematic servants
debug_context("アルトリア・ペンドラゴン")
debug_context("光のコヤンスカヤ")
debug_context("オベロン")
