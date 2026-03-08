
import database

def check_supports():
    ids = [504800, 901300, 901400, 503600]
    print("Checking other support IDs...")
    for i in ids:
        svt = database.get_servant_detail(i)
        if svt:
            print(f"ID: {i} -> {svt['name']} ({svt['class_name']})")
        else:
            print(f"ID: {i} -> NOT FOUND")

if __name__ == "__main__":
    check_supports()
