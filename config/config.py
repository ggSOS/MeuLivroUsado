"""
Configurações da aplicação Flask
"""

import os

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE = os.environ.get('DATABASE_PATH') or 'biblioteca.db'
    
class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY deve ser definida em produção")

class TestingConfig(Config):
    """Configuração de teste"""
    DEBUG = True
    TESTING = True
    DATABASE = ':memory:'  # Banco em memória para testes

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}