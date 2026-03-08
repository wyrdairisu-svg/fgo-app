import database
import json

def check_class_id(name):
    res = database.search_servants(name, limit=1)
    if res:
        svt = res[0]
        data = json.loads(svt['json_data'])
        print(f"{name} ({svt['class_name']}): ClassID = {data.get('classId')}")

if __name__ == "__main__":
    check_class_id("アルトリア") # Saber
    check_class_id("エミヤ") # Archer
    check_class_id("クー・フーリン") # Lancer
    check_class_id("メドゥーサ") # Rider
    check_class_id("メディア") # Caster
    check_class_id("佐々木小次郎") # Assassin
    check_class_id("ヘラクレス") # Berserker
    check_class_id("ジャンヌ") # Ruler
    check_class_id("巌窟王") # Avenger
    check_class_id("BB") # MoonCancer
    check_class_id("メルトリリス") # AlterEgo
    check_class_id("アビゲイル") # Foreigner
    check_class_id("マシュ") # Shielder
    check_class_id("オベロン") # Pretender
