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


if __name__ == '__main__':
    private_pem_str, public_pem_str = generate_key_pair_strings()

    days_later = 30
    timestamp = generate_timestamp(days_later)
    print(timestamp)
    # 加密消息
    ciphertext_str = encrypt_message(str(timestamp), public_pem_str)
    print("加密后的字符串:", ciphertext_str)

    # 解密消息
    plaintext_str = decrypt_message(ciphertext_str, private_pem_str)
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
