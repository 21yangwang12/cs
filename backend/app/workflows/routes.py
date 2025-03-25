from flask import Blueprint, request, jsonify
from models.workflow import Workflow, WorkflowVersion, WorkflowExecution, ExecutionLog
from models.database import db
from app.auth.routes import token_required
from datetime import datetime

workflows_bp = Blueprint('workflows', __name__)

@workflows_bp.route('', methods=['GET'])
@token_required
def get_workflows(current_user):
    workflows = Workflow.query.filter_by(creator_id=current_user.id).all()
    return jsonify({
        'workflows': [workflow.to_dict() for workflow in workflows]
    }), 200

@workflows_bp.route('', methods=['POST'])
@token_required
def create_workflow(current_user):
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('name',)):
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 创建新工作流
    workflow = Workflow(
        name=data['name'],
        description=data.get('description', ''),
        creator_id=current_user.id
    )
    
    db.session.add(workflow)
    db.session.commit()
    
    return jsonify(workflow.to_dict()), 201

@workflows_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_workflow(current_user, id):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权访问此工作流'}), 403
    
    result = workflow.to_dict()
    result['versions'] = [
        {
            'id': version.id,
            'version': version.version,
            'status': version.status,
            'created_at': version.created_at.isoformat()
        } for version in workflow.versions
    ]
    
    return jsonify(result), 200

@workflows_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_workflow(current_user, id):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权修改此工作流'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        workflow.name = data['name']
    
    if 'description' in data:
        workflow.description = data['description']
    
    db.session.commit()
    
    return jsonify(workflow.to_dict()), 200

@workflows_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_workflow(current_user, id):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权删除此工作流'}), 403
    
    db.session.delete(workflow)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '工作流已删除'
    }), 200

@workflows_bp.route('/<int:id>/versions', methods=['GET'])
@token_required
def get_workflow_versions(current_user, id):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权访问此工作流'}), 403
    
    versions = WorkflowVersion.query.filter_by(workflow_id=id).all()
    
    return jsonify({
        'versions': [version.to_dict() for version in versions]
    }), 200

@workflows_bp.route('/<int:id>/versions', methods=['POST'])
@token_required
def create_workflow_version(current_user, id):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权修改此工作流'}), 403
    
    data = request.get_json()
    
    # 验证必要字段
    if 'definition' not in data:
        return jsonify({'message': '缺少必要字段'}), 400
    
    # 获取最新版本号
    latest_version = WorkflowVersion.query.filter_by(workflow_id=id).order_by(WorkflowVersion.version.desc()).first()
    new_version_number = 1 if not latest_version else latest_version.version + 1
    
    # 创建新版本
    version = WorkflowVersion(
        workflow_id=id,
        version=new_version_number,
        definition=data['definition'],
        status='draft'
    )
    
    db.session.add(version)
    db.session.commit()
    
    return jsonify(version.to_dict()), 201

@workflows_bp.route('/<int:id>/versions/<int:version>', methods=['GET'])
@token_required
def get_workflow_version(current_user, id, version):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权访问此工作流'}), 403
    
    workflow_version = WorkflowVersion.query.filter_by(workflow_id=id, version=version).first_or_404()
    
    return jsonify(workflow_version.to_dict()), 200

@workflows_bp.route('/<int:id>/versions/<int:version>/publish', methods=['PUT'])
@token_required
def publish_workflow_version(current_user, id, version):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权修改此工作流'}), 403
    
    workflow_version = WorkflowVersion.query.filter_by(workflow_id=id, version=version).first_or_404()
    workflow_version.status = 'published'
    
    db.session.commit()
    
    return jsonify(workflow_version.to_dict()), 200

@workflows_bp.route('/<int:id>/versions/<int:version>/archive', methods=['PUT'])
@token_required
def archive_workflow_version(current_user, id, version):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权修改此工作流'}), 403
    
    workflow_version = WorkflowVersion.query.filter_by(workflow_id=id, version=version).first_or_404()
    workflow_version.status = 'archived'
    
    db.session.commit()
    
    return jsonify(workflow_version.to_dict()), 200

@workflows_bp.route('/<int:id>/versions/<int:version>/execute', methods=['POST'])
@token_required
def execute_workflow(current_user, id, version):
    workflow = Workflow.query.get_or_404(id)
    
    # 检查权限
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权执行此工作流'}), 403
    
    workflow_version = WorkflowVersion.query.filter_by(workflow_id=id, version=version).first_or_404()
    
    # 检查版本状态
    if workflow_version.status != 'published':
        return jsonify({'message': '只能执行已发布的工作流版本'}), 400
    
    data = request.get_json() or {}
    input_params = data.get('input_params', {})
    
    # 创建执行记录
    execution = WorkflowExecution(
        version_id=workflow_version.id,
        status='running',
        started_at=datetime.utcnow()
    )
    
    db.session.add(execution)
    db.session.commit()
    
    # 在实际应用中，这里应该启动异步任务来执行工作流
    # 为了演示，我们直接返回执行ID
    
    return jsonify({
        'execution_id': execution.id,
        'status': execution.status,
        'started_at': execution.started_at.isoformat()
    }), 200

@workflows_bp.route('/executions/<int:id>', methods=['GET'])
@token_required
def get_execution(current_user, id):
    execution = WorkflowExecution.query.get_or_404(id)
    
    # 检查权限
    workflow_version = WorkflowVersion.query.get(execution.version_id)
    workflow = Workflow.query.get(workflow_version.workflow_id)
    
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权访问此执行记录'}), 403
    
    return jsonify({
        'id': execution.id,
        'workflow_id': workflow.id,
        'version_id': workflow_version.id,
        'status': execution.status,
        'started_at': execution.started_at.isoformat(),
        'ended_at': execution.ended_at.isoformat() if execution.ended_at else None,
        'result': execution.result
    }), 200

@workflows_bp.route('/executions/<int:id>/logs', methods=['GET'])
@token_required
def get_execution_logs(current_user, id):
    execution = WorkflowExecution.query.get_or_404(id)
    
    # 检查权限
    workflow_version = WorkflowVersion.query.get(execution.version_id)
    workflow = Workflow.query.get(workflow_version.workflow_id)
    
    if workflow.creator_id != current_user.id:
        return jsonify({'message': '无权访问此执行记录'}), 403
    
    logs = ExecutionLog.query.filter_by(execution_id=id).all()
    
    return jsonify({
        'logs': [log.to_dict() for log in logs]
    }), 200
