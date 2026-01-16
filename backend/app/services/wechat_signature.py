"""
微信签名验证工具

用于微信公众平台服务器配置的签名验证。
"""

import hashlib
from typing import List


def verify_signature(signature: str, timestamp: str, nonce: str, token: str) -> bool:
    """验证微信签名

    Args:
        signature: 微信加密签名
        timestamp: 时间戳
        nonce: 随机数
        token: 开发者填写的 token

    Returns:
        True: 验证成功
        False: 验证失败
    """
    # 1. 将 token、timestamp、nonce 三个参数进行字典序排序
    params: List[str] = sorted([token, timestamp, nonce])

    # 2. 将三个参数字符串拼接成一个字符串进行 sha1 加密
    sorted_str = "".join(params)
    sha1 = hashlib.sha1()
    sha1.update(sorted_str.encode("utf-8"))
    hashcode = sha1.hexdigest()

    # 3. 开发者获得加密后的字符串可与 signature 对比
    return hashcode == signature
