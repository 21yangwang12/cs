from datetime import datetime
from models.database import db
from models.user import User

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    versions = db.relationship('WorkflowVersion', backref='workflow', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WorkflowVersion(db.Model):
    __tablename__ = 'workflow_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    definition = db.Column(db.JSON, nullable=False)
    status = db.Column(db.Enum('draft', 'published', 'archived', name='version_status'), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    nodes = db.relationship('WorkflowNode', backref='version', lazy=True, cascade='all, delete-orphan')
    executions = db.relationship('WorkflowExecution', backref='version', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('workflow_id', 'version', name='uix_workflow_version'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'version': self.version,
            'definition': self.definition,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class WorkflowNode(db.Model):
    __tablename__ = 'workflow_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('workflow_versions.id'), nullable=False)
    node_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.JSON, nullable=False)
    position = db.Column(db.JSON, nullable=False)
    next_nodes = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'version_id': self.version_id,
            'node_type': self.node_type,
            'config': self.config,
            'position': self.position,
            'next_nodes': self.next_nodes
        }

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('workflow_versions.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed', name='execution_status'), default='pending')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    result = db.Column(db.JSON)
    
    # 关系
    logs = db.relationship('ExecutionLog', backref='execution', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'version_id': self.version_id,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'result': self.result
        }

class ExecutionLog(db.Model):
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_nodes.id'))
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.Enum('info', 'warning', 'error', name='log_level'), default='info')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'node_id': self.node_id,
            'message': self.message,
            'level': self.level,
            'timestamp': self.timestamp.isoformat()
        }
