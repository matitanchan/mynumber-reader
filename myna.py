#参考:https://tex2e.github.io/blog/protocol/jpki-mynumbercard-with-apdu

import nfc
import binascii
import sys
import re
import getpass

clf = nfc.ContactlessFrontend('usb')
print("マイナンバーカードをリーダーにセットしてください")
tag = clf.connect(rdwr={'on-connect': lambda tag: False})

data = bytearray.fromhex("00A4040C0AD3921000310001010408")
tag.transceive(data)

authtype = input("照合番号Bの場合は1を、暗証番号の場合は2を押してください。:")

if authtype=="1":

    birth = input("生年月日を入力してください。(例:令和2年2月24日生の場合:020224):")
    exp = input("有効期限を入力してください。:")
    seccode = input("セキュリティコードを入力してください。:")

    code = birth + exp + seccode
    code = code.encode()
    code = code.hex()

    data = bytearray.fromhex("00A4020C020015")
    tag.transceive(data)

    data = bytearray.fromhex('002000800E' + code)
    result = tag.transceive(data)
elif authtype=="2":
    pin = getpass.getpass(prompt='暗証番号を入力してください(セキュリティのため表示されません):')

    code = pin.encode()
    code = code.hex()

    data = bytearray.fromhex("00A4020C020011")
    tag.transceive(data)

    data = bytearray.fromhex('0020008004' + code)
    result = tag.transceive(data)
else:
    print("不明な数字が入力されました")
    sys.exit()

resulthex = result.hex()[:3]

if result == bytearray(b'\x90\x00'):
    print('認証に成功しました')
elif result == bytearray(b'i\x84'):
    print("券面補助入力APがブロックされています。住民票のある市区町村の窓口で解除してください。")
    sys.exit()
elif resulthex == "63c":
    print('照合番号Bまたは暗証番号が違います。')
    result = result.hex()[3]
    print("リトライ可能数:" + result + "回")
    sys.exit()
else:
    print("不明なエラーです。最初からやり直してください。")
    sys.exit()

data = bytearray.fromhex("00A4020C020002")
tag.transceive(data)

data = bytearray.fromhex("00B0000201")
tag.transceive(data)

data = bytearray.fromhex("00B0000003")
result = tag.transceive(data)
a = result.hex()
a = a[4:6]
a = "0x" + a
a = int(a, 16) + 0x03
a = format(a, 'x')
data = bytearray.fromhex("00B00000" + a)
result = tag.transceive(data)
result = result.hex()
name = binascii.unhexlify(re.search(r"df22(.*?)df23", result).group(1)).decode('utf-8')
name = name[1:]
address = binascii.unhexlify(re.search(r"df23(.*?)df24", result).group(1)).decode('utf-8')
address = address[1:]
birth = binascii.unhexlify(re.search(r"df24(.*?)df25", result).group(1)).decode('utf-8')
birth = birth[1:]
sex = re.search(r"df25(.*?)9000", result).group(1)
sex = sex[2:]

if sex=="31":
    sex = "男"
elif sex=="32":
    sex = "女"
elif sex=="33":
    sex = "その他"

birth = birth[0:4] + "年" + birth[4:6] + "月" + birth[6:8] + "日"

print("名前:" + name)
print("住所:" + address)
print("生年月日:" + birth)
print("性別:" + sex)
clf.close()