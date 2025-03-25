from flask import Blueprint

workflows_bp = Blueprint('workflows', __name__)

# 导入路由，确保它们被注册
from app.workflows.routes import *
