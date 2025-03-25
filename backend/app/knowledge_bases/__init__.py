from flask import Blueprint

kb_bp = Blueprint('knowledge_bases', __name__)

# 导入路由，确保它们被注册
from app.knowledge_bases.routes import *
