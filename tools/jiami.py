import datetime
import time
import base64
import re
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def generate_key_pair_strings():
    """生成 RSA 密钥对，并返回 PEM 格式的字符串"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # 将私钥转换为 PEM 格式字符串
    private_pem_str = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    # 将公钥转换为 PEM 格式字符串
    public_pem_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    print(private_pem_str)
    print(public_pem_str)
    return private_pem_str, public_pem_str


# 公钥加密
def encrypt_message(message, public_pem_str):
    """使用公钥字符串加密消息"""
    public_key = serialization.load_pem_public_key(public_pem_str.encode("utf-8"))
    message_bytes = message.encode("utf-8")
    ciphertext = public_key.encrypt(
        message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    ciphertext_str = base64.b64encode(ciphertext).decode("utf-8")
    return ciphertext_str


# 私钥解密
def decrypt_message(ciphertext_str, private_pem_str):
    """使用私钥字符串解密消息"""
    private_key = serialization.load_pem_private_key(
        private_pem_str.encode("utf-8"),
        password=None,
    )
    ciphertext = base64.b64decode(ciphertext_str.encode("utf-8"))
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    plaintext_str = plaintext.decode("utf-8")
    return plaintext_str


def generate_timestamp(d):
    future_date = datetime.datetime.now() + datetime.timedelta(days=d)
    return "expiration_" + str(int(time.mktime(future_date.timetuple())))


def extract_and_convert_timestamp(input_string):
    """
    从输入字符串中提取时间戳并转换为时间，要求字符串以 "expiration_" 开头

    Args:
        input_string: 输入字符串，格式为 "expiration_时间戳"

    Returns:
        datetime 对象，表示提取的时间戳对应的时间
        如果提取失败或字符串不以 "expiration_" 开头，返回 None
    """

    # 判断字符串是否以 "expiration_" 开头
    if not input_string.startswith("expiration_"):
        return None

    # 使用正则表达式提取时间戳
    match = re.search(r"expiration_(\d+)", input_string)
    if match:
        timestamp_str = match.group(1)
        try:
            timestamp = int(timestamp_str)
            dt = datetime.datetime.fromtimestamp(timestamp)
            return dt
        except ValueError:
            return None
    else:
        return None


privateKey = """
-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDVLOXv9jUG35lf
x7C0hI2CwcJvZQUbwowPdKHpyoOceCP23fZrntCJV2aNXnuDtmfCmirgLI3N814L
3m/IN3pbCOY8SVbKXWpeWTUHKQgluQqQREkDU6InflKkiMF2/rJWDY2m5tkhgYM4
0dzk25U43xEABZy1KnWCfQQQypAtpCQOD4Mb96UueY5idhlwLfkoDq0IIIRlKSD+
Gzs9iY0HXMV+V86hqz/cRgy6gdx2hyMyHjcWg5O/9n+iITSo138UxCHDUvrxR8Q0
fJ1vJwDEj1DdqIHx7CMa0PRexa6AvEr/LTlcGOKBnPijw5Gbgw88wAgurGC0I6XS
AHl+MJZDAgMBAAECggEAB/duE7omlX5XW9TOyJLoO5nkcMechG2QULw3QtFD0DNN
229vF+rZozr7b6QMx0l9S4X5vTfyXV8kxW/Hdfrbco8najBZcyWWOza9PGpu+K3s
yaMWUW6s3Cn536vmraeWCuY7GXYoviT6E5kFgXNSpSCc9jG/f1EPZCl/ieXFXpc2
xOaQeLx+v3M+vY8YgCpdJuO6vK/V3efVUhWUncz41ObunvUhGXx9tZQv4Qzfalz1
lHQpd6iRM7PIn/grT369nRnsYvKlEx/hIiqlyLpu3HxrB80ebVevM0aOoxz93+9M
JaTs8v7unPGQ/s5vqe9jCNZaXiE/ZUHAIa24okZjrQKBgQD2T8P38HnhwLL2yyZl
JkgAzfqKzmP/+ocmvQkyHuLspWxiP/vzq+Zgmk2jBOCCXJosM5mtROsfqVjZeToG
2XYnTzvbck67HEn4fjGlBGWCBTXPcc77Yp6pnkAZ+AWBfTqUdHxCjbvmcxc6rVAT
g5op6RcNWEPEFnvyy9snvgr71QKBgQDdj3e8gl9q+KNvLXqobr2AyIExUh45tT4v
OOkO4YvsgfLOiHDtukjd/v90kp9wce6A+gzUicznqktRjg2HJQiN/AnVyn08LigD
srEzigDuwTyaQgqYBQECgY5e/cs0WwdXFNTS7WKDV8sZ2pFEmbmVdqK0TVivueEL
CrDLDXnNtwKBgQDUAGPUDA9b19gxwzkQ5poi1ydGQc6gjKm3Fg3MLflzZg6boibh
3Js1mpooLhJvIfUxBljHYgJeBgyLYmQncRTZUMFcaE6LjhW85CEmv1n/RyzBmFtm
08NsiuDxeSCEC51YGcq6HfQUrgrYXkQGB8exOwa0Xbw2EoQsvnmrA0/A4QKBgQDE
sEyXqRWUHU7ZsAIn7MeGwHkQk9oJWQDvYxJjB4/0Uhh/iVjXcnylt26IynGInVwi
W9lwBTVGpENhDz6rLxE9GvaQOMac2kzjm4r8OhNB4YIvX1mQQ0D2PJVrdtsii30k
rXWSGvNNrm67cPFteRrruPoQHmoQ9m72InN4j2oGWQKBgQDRgrT4zH2WzOeP4Gcg
7IlO4QmXLP2GQ4082YsiHw6jQV9xV8Ae6miJbKbLpWpNy6/pbS+/7kAv3cP8vjX3
SGcY6bTvTalstJfiGi2j5arCFKnt1KEyHH98UCu6reR96WSZe+z1+fksqEg/fGC5
anPr6Cll/DsAcaY61iX+B1Rxsg==
-----END PRIVATE KEY-----
"""

publicKey = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1Szl7/Y1Bt+ZX8ewtISN
gsHCb2UFG8KMD3Sh6cqDnHgj9t32a57QiVdmjV57g7Znwpoq4CyNzfNeC95vyDd6
WwjmPElWyl1qXlk1BykIJbkKkERJA1OiJ35SpIjBdv6yVg2NpubZIYGDONHc5NuV
ON8RAAWctSp1gn0EEMqQLaQkDg+DG/elLnmOYnYZcC35KA6tCCCEZSkg/hs7PYmN
B1zFflfOoas/3EYMuoHcdocjMh43FoOTv/Z/oiE0qNd/FMQhw1L68UfENHydbycA
xI9Q3aiB8ewjGtD0XsWugLxK/y05XBjigZz4o8ORm4MPPMAILqxgtCOl0gB5fjCW
QwIDAQAB
-----END PUBLIC KEY-----
"""

if __name__ == '__main__':
    # private_pem_str, public_pem_str = generate_key_pair_strings()

    days_later = 360
    timestamp = generate_timestamp(days_later)
    print(timestamp)
    # 加密消息
    ciphertext_str = encrypt_message(str(timestamp), publicKey)
    print("加密后的字符串:", ciphertext_str)

    # 解密消息
    plaintext_str = decrypt_message(ciphertext_str, privateKey)
    print("解密后的字符串:", plaintext_str)

    date = extract_and_convert_timestamp(plaintext_str)
    if date:
        # 格式化输出日期和时间
        formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
        print(formatted_date)
    else:
        print("提取时间戳失败")
    if datetime.datetime.now() > date:
        print("失效")
    else:
        print("有效")
