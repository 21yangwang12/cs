from flask import Blueprint

ai_bp = Blueprint('ai', __name__)

# 导入路由，确保它们被注册
from app.ai.routes import *
