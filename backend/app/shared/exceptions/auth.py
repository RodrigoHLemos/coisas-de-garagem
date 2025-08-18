"""
Exceções customizadas para autenticação
Seguindo o princípio de Single Responsibility
"""


class AuthException(Exception):
    """Exceção base para autenticação"""
    pass


class InvalidCredentialsError(AuthException):
    """Erro quando as credenciais são inválidas"""
    pass


class UserAlreadyExistsError(AuthException):
    """Erro quando o usuário já existe"""
    pass


class UserNotFoundError(AuthException):
    """Erro quando o usuário não é encontrado"""
    pass


class TokenExpiredError(AuthException):
    """Erro quando o token expirou"""
    pass


class InvalidTokenError(AuthException):
    """Erro quando o token é inválido"""
    pass


class InsufficientPermissionsError(AuthException):
    """Erro quando o usuário não tem permissões suficientes"""
    pass


class EmailNotVerifiedError(AuthException):
    """Erro quando o email não foi verificado"""
    pass


class SessionExpiredError(AuthException):
    """Erro quando a sessão expirou"""
    pass


class PasswordTooWeakError(AuthException):
    """Erro quando a senha é muito fraca"""
    pass