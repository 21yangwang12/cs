from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# 导入路由，确保它们被注册
from app.auth.routes import *
