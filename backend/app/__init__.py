from flask import Flask
from flask_cors import CORS
from config.config import Config
from models.database import db
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    
    # 注册蓝图
    from app.auth.routes import auth_bp
    from app.workflows.routes import workflows_bp
    from app.ai.routes import ai_bp
    from app.knowledge_bases.routes import kb_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(workflows_bp, url_prefix='/api/workflows')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(kb_bp, url_prefix='/api/knowledge-bases')
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Service is running'}
    
    return app
