import pytest
from app.services.auth_service import AuthService
from app.core.security import get_password_hash, verify_password


class TestPasswordSecurity:
    """密码安全测试"""

    def test_password_hash(self):
        """测试密码哈希"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_different(self):
        """测试相同密码的哈希值不同（salt）"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_empty_password(self):
        """测试空密码验证"""
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True
        assert verify_password("password", hashed) is False


class TestAuthService:
    """认证服务测试"""

    async def test_create_token(self):
        """测试Token创建"""
        service = AuthService()
        user_id = "test-user-id-123"
        token = service.create_token(user_id)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_register_validation(self, db_session):
        """测试注册验证"""
        service = AuthService()

        # 注册用户
        user = await service.register(
            username="serviceuser",
            email=None,
            phone=None,
            password="testpass123",
            nickname="服务测试",
            db=db_session
        )
        assert user is not None
        assert user.username == "serviceuser"
        assert user.nickname == "服务测试"

        # 尝试重复注册
        with pytest.raises(ValueError, match="用户名已存在"):
            await service.register(
                username="serviceuser",
                email=None,
                phone=None,
                password="testpass123",
                nickname="另一个",
                db=db_session
            )

    async def test_register_with_email(self, db_session):
        """测试邮箱注册"""
        service = AuthService()

        user = await service.register(
            username=None,
            email="emailuser@example.com",
            phone=None,
            password="testpass123",
            nickname="邮箱用户",
            db=db_session
        )
        assert user.email == "emailuser@example.com"

    async def test_register_duplicate_email(self, db_session):
        """测试重复邮箱注册"""
        service = AuthService()

        await service.register(
            username="user1",
            email="duplicate@example.com",
            phone=None,
            password="testpass123",
            nickname="用户1",
            db=db_session
        )

        with pytest.raises(ValueError, match="邮箱已被注册"):
            await service.register(
                username="user2",
                email="duplicate@example.com",
                phone=None,
                password="testpass123",
                nickname="用户2",
                db=db_session
            )

    async def test_register_with_phone(self, db_session):
        """测试手机号注册"""
        service = AuthService()

        user = await service.register(
            username=None,
            email=None,
            phone="13800138000",
            password="testpass123",
            nickname="手机用户",
            db=db_session
        )
        assert user.phone == "13800138000"

    async def test_login_password_success(self, db_session):
        """测试密码登录成功"""
        service = AuthService()

        # 先注册用户
        await service.register(
            username="loginuser",
            email=None,
            phone=None,
            password="password123",
            nickname="登录用户",
            db=db_session
        )

        # 登录
        user = await service.login_password("loginuser", "password123", db_session)
        assert user is not None
        assert user.username == "loginuser"

    async def test_login_password_wrong_password(self, db_session):
        """测试密码登录错误密码"""
        service = AuthService()

        await service.register(
            username="loginuser2",
            email=None,
            phone=None,
            password="password123",
            nickname="登录用户2",
            db=db_session
        )

        with pytest.raises(ValueError, match="用户名或密码错误"):
            await service.login_password("loginuser2", "wrongpassword", db_session)

    async def test_login_password_nonexistent_user(self, db_session):
        """测试密码登录不存在的用户"""
        service = AuthService()

        with pytest.raises(ValueError, match="用户名或密码错误"):
            await service.login_password("nonexistent", "password123", db_session)
