import pytest
from app.services.sms_service import SmsService


class TestSmsService:
    """短信服务测试"""

    def test_md5_encryption(self):
        """测试 MD5 加密"""
        sms_service = SmsService()

        # 测试 MD5 加密
        result = sms_service._md5("test123")
        assert len(result) == 32  # MD5 结果应该是 32 位十六进制字符串

        # 相同输入应该产生相同输出
        result2 = sms_service._md5("test123")
        assert result == result2

        # 不同输入应该产生不同输出
        result3 = sms_service._md5("test456")
        assert result != result3

    def test_status_map(self):
        """测试状态码映射"""
        sms_service = SmsService()

        # 检查所有状态码都有对应说明
        assert '0' in sms_service.STATUS_MAP
        assert sms_service.STATUS_MAP['0'] == '短信发送成功'
        assert '-1' in sms_service.STATUS_MAP
        assert '30' in sms_service.STATUS_MAP
        assert '40' in sms_service.STATUS_MAP
        assert '41' in sms_service.STATUS_MAP

    @pytest.mark.asyncio
    async def test_send_sms_missing_config(self):
        """测试缺少配置或无效配置时的错误处理"""
        sms_service = SmsService()

        # 使用无效配置发送短信应该抛出异常
        with pytest.raises(ValueError) as exc_info:
            await sms_service._send_sms("13800138000", "123456")

        # 应该抛出 ValueError
        assert exc_info.type is ValueError
        # 错误信息应该包含"短信"字样
        assert "短信" in str(exc_info.value) or "配置" in str(exc_info.value)

    def test_status_map_completeness(self):
        """测试状态码映射完整性"""
        sms_service = SmsService()

        # 确保所有状态码都有映射
        expected_codes = ['0', '-1', '-2', '30', '40', '41', '42', '43', '50']
        for code in expected_codes:
            assert code in sms_service.STATUS_MAP, f"状态码 {code} 缺少映射"
            assert isinstance(sms_service.STATUS_MAP[code], str)
            assert len(sms_service.STATUS_MAP[code]) > 0
