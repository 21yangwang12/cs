from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from models.knowledge_base import KnowledgeBase, KBFile, KBIndex
from models.database import db
from app.auth.routes import token_required
import uuid
import requests
from config.config import Config

kb_bp = Blueprint('knowledge_bases', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'csv', 'md'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@kb_bp.route('', methods=['GET'])
@token_required
def get_knowledge_bases(current_user):
    knowledge_bases = KnowledgeBase.query.filter_by(creator_id=current_user.id).all()
    return jsonify({
        'knowledge_bases': [kb.to_dict() for kb in knowledge_bases]
    }), 200

@kb_bp.route('', methods=['POST'])
@token_required
def create_knowledge_base(current_user):
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('name',)):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 创建新知识库
    kb = KnowledgeBase(
        name=data['name'],
        description=data.get('description', ''),
        creator_id=current_user.id
    )
    
    db.session.add(kb)
    db.session.commit()
    
    return jsonify(kb.to_dict()), 201

@kb_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_knowledge_base(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权访问此知识库'}), 403
    
    result = kb.to_dict()
    result['files'] = [file.to_dict() for file in kb.files]
    
    return jsonify(result), 200

@kb_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_knowledge_base(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权修改此知识库'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        kb.name = data['name']
    
    if 'description' in data:
        kb.description = data['description']
    
    db.session.commit()
    
    return jsonify(kb.to_dict()), 200

@kb_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_knowledge_base(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权删除此知识库'}), 403
    
    # 删除关联的文件
    for file in kb.files:
        try:
            os.remove(file.file_path)
        except:
            pass
    
    db.session.delete(kb)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '知识库已删除'
    }), 200

@kb_bp.route('/<int:id>/files', methods=['GET'])
@token_required
def get_knowledge_base_files(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权访问此知识库'}), 403
    
    files = KBFile.query.filter_by(kb_id=id).all()
    
    return jsonify({
        'files': [file.to_dict() for file in files]
    }), 200

@kb_bp.route('/<int:id>/files', methods=['POST'])
@token_required
def upload_file(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权修改此知识库'}), 403
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'message': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 安全处理文件名
        filename = secure_filename(file.filename)
        
        # 创建唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保上传目录存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件类型
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # 创建文件记录
        kb_file = KBFile(
            kb_id=id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path
        )
        
        db.session.add(kb_file)
        db.session.commit()
        
        # 异步处理文件索引
        # 在实际应用中，这里应该启动异步任务来处理文件索引
        # 为了演示，我们直接返回文件信息
        
        return jsonify(kb_file.to_dict()), 201
    
    return jsonify({'message': '不支持的文件类型'}), 400

@kb_bp.route('/<int:id>/files/<int:file_id>', methods=['GET'])
@token_required
def get_file(current_user, id, file_id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权访问此知识库'}), 403
    
    kb_file = KBFile.query.get_or_404(file_id)
    
    # 检查文件是否属于该知识库
    if kb_file.kb_id != id:
        return jsonify({'message': '文件不属于该知识库'}), 404
    
    return jsonify(kb_file.to_dict()), 200

@kb_bp.route('/<int:id>/files/<int:file_id>', methods=['DELETE'])
@token_required
def delete_file(current_user, id, file_id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权修改此知识库'}), 403
    
    kb_file = KBFile.query.get_or_404(file_id)
    
    # 检查文件是否属于该知识库
    if kb_file.kb_id != id:
        return jsonify({'message': '文件不属于该知识库'}), 404
    
    # 删除物理文件
    try:
        os.remove(kb_file.file_path)
    except:
        pass
    
    # 删除数据库记录
    db.session.delete(kb_file)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '文件已删除'
    }), 200

@kb_bp.route('/<int:id>/query', methods=['POST'])
@token_required
def query_knowledge_base(current_user, id):
    kb = KnowledgeBase.query.get_or_404(id)
    
    # 检查权限
    if kb.creator_id != current_user.id:
        return jsonify({'message': '无权访问此知识库'}), 403
    
    data = request.get_json()
    
    # 验证必要字段
    if 'query' not in data:
        return jsonify({'message': '缺少查询内容'}), 400
    
    query = data['query']
    
    # 调用DeepSeek API进行知识库查询
    try:
        # 获取知识库中的文件
        files = KBFile.query.filter_by(kb_id=id).all()
        
        if not files:
            return jsonify({'message': '知识库中没有文件'}), 400
        
        # 构建知识库内容
        kb_content = ""
        for file in files:
            # 读取文件内容
            try:
                with open(file.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    kb_content += f"\n--- {file.filename} ---\n{content}\n"
            except:
                # 如果无法读取文件，跳过
                continue
        
        # 构建请求内容
        prompt = f"""
        请根据以下知识库内容回答用户的问题：
        
        知识库内容：
        {kb_content[:10000]}  # 限制内容长度
        
        用户问题：{query}
        
        请只根据知识库中的内容回答，如果知识库中没有相关信息，请明确说明。
        """
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return jsonify({'message': 'DeepSeek API调用失败', 'error': response.text}), 500
        
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        return jsonify({
            'query': query,
            'answer': answer,
            'sources': [file.filename for file in files]
        }), 200
            
    except Exception as e:
        return jsonify({'message': f'查询知识库时发生错误: {str(e)}'}), 500
