from flask import Blueprint, request, jsonify
import requests
import json
from models.database import db
from app.auth.routes import token_required
from config.config import Config

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_workflow(current_user):
    data = request.get_json()
    
    # 验证必要字段
    if 'description' not in data:
        return jsonify({'message': '缺少工作流描述'}), 400
    
    description = data['description']
    knowledge_base_id = data.get('knowledge_base_id')
    
    # 调用DeepSeek API进行工作流分析
    try:
        # 构建请求内容
        prompt = f"""
        请分析以下工作流需求，并将其拆解为具体步骤：
        
        {description}
        
        请返回JSON格式的结果，包含以下字段：
        1. analysis_id: 分析ID（随机字符串）
        2. steps: 步骤数组，每个步骤包含id、description、is_uncertain和options字段
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
            'temperature': 0.7,
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
        content = result['choices'][0]['message']['content']
        
        # 解析返回的JSON内容
        try:
            analysis_result = json.loads(content)
            return jsonify(analysis_result), 200
        except json.JSONDecodeError:
            # 如果返回内容不是有效的JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                try:
                    analysis_result = json.loads(json_match.group(1))
                    return jsonify(analysis_result), 200
                except json.JSONDecodeError:
                    pass
            
            # 如果仍然无法解析，返回错误
            return jsonify({'message': 'DeepSeek API返回的内容无法解析为JSON'}), 500
            
    except Exception as e:
        return jsonify({'message': f'分析工作流时发生错误: {str(e)}'}), 500

@ai_bp.route('/confirm', methods=['POST'])
@token_required
def confirm_workflow_steps(current_user):
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('analysis_id', 'confirmations')):
        return jsonify({'message': '缺少必要字段'}), 400
    
    analysis_id = data['analysis_id']
    confirmations = data['confirmations']
    
    # 调用DeepSeek API更新工作流步骤
    try:
        # 构建请求内容
        prompt = f"""
        请根据用户的确认，更新工作流步骤：
        
        分析ID: {analysis_id}
        用户确认:
        {json.dumps(confirmations, indent=2, ensure_ascii=False)}
        
        请返回更新后的JSON格式结果，包含以下字段：
        1. analysis_id: 与输入相同的分析ID
        2. updated_steps: 更新后的步骤数组，每个步骤包含id、description、is_uncertain和options字段
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
            'temperature': 0.7,
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
        content = result['choices'][0]['message']['content']
        
        # 解析返回的JSON内容
        try:
            updated_result = json.loads(content)
            return jsonify(updated_result), 200
        except json.JSONDecodeError:
            # 如果返回内容不是有效的JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                try:
                    updated_result = json.loads(json_match.group(1))
                    return jsonify(updated_result), 200
                except json.JSONDecodeError:
                    pass
            
            # 如果仍然无法解析，返回错误
            return jsonify({'message': 'DeepSeek API返回的内容无法解析为JSON'}), 500
            
    except Exception as e:
        return jsonify({'message': f'确认工作流步骤时发生错误: {str(e)}'}), 500

@ai_bp.route('/generate', methods=['POST'])
@token_required
def generate_workflow(current_user):
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('analysis_id', 'workflow_id')):
        return jsonify({'message': '缺少必要字段'}), 400
    
    analysis_id = data['analysis_id']
    workflow_id = data['workflow_id']
    
    # 调用DeepSeek API生成工作流定义
    try:
        # 构建请求内容
        prompt = f"""
        请根据分析ID {analysis_id} 生成完整的工作流定义。
        
        工作流定义应该是一个JSON对象，包含以下结构：
        {{
          "nodes": [
            {{
              "id": "node-1",
              "type": "start",
              "position": {{"x": 100, "y": 100}},
              "data": {{}}
            }},
            // 其他节点...
          ],
          "edges": [
            {{
              "id": "edge-1-2",
              "source": "node-1",
              "target": "node-2"
            }},
            // 其他边...
          ]
        }}
        
        请确保生成的工作流定义是有效的JSON格式，并且节点和边的连接关系正确。
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
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return jsonify({'message': 'DeepSeek API调用失败', 'error': response.text}), 500
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 解析返回的JSON内容
        try:
            # 尝试直接解析内容
            workflow_definition = json.loads(content)
        except json.JSONDecodeError:
            # 如果返回内容不是有效的JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                try:
                    workflow_definition = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    return jsonify({'message': 'DeepSeek API返回的内容无法解析为JSON'}), 500
            else:
                return jsonify({'message': 'DeepSeek API返回的内容无法解析为JSON'}), 500
        
        # 创建工作流版本
        from models.workflow import Workflow, WorkflowVersion
        
        workflow = Workflow.query.get(workflow_id)
        if not workflow:
            return jsonify({'message': '工作流不存在'}), 404
        
        if workflow.creator_id != current_user.id:
            return jsonify({'message': '无权修改此工作流'}), 403
        
        # 获取最新版本号
        latest_version = WorkflowVersion.query.filter_by(workflow_id=workflow_id).order_by(WorkflowVersion.version.desc()).first()
        new_version_number = 1 if not latest_version else latest_version.version + 1
        
        # 创建新版本
        version = WorkflowVersion(
            workflow_id=workflow_id,
            version=new_version_number,
            definition=workflow_definition,
            status='draft'
        )
        
        db.session.add(version)
        db.session.commit()
        
        return jsonify({
            'workflow_id': workflow_id,
            'version_id': version.id,
            'definition': workflow_definition
        }), 201
            
    except Exception as e:
        return jsonify({'message': f'生成工作流定义时发生错误: {str(e)}'}), 500
