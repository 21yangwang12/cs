from datetime import datetime
from models.database import db
from models.user import User

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_bases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    files = db.relationship('KBFile', backref='knowledge_base', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'file_count': len(self.files)
        }

class KBFile(db.Model):
    __tablename__ = 'kb_files'
    
    id = db.Column(db.Integer, primary_key=True)
    kb_id = db.Column(db.Integer, db.ForeignKey('knowledge_bases.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    indices = db.relationship('KBIndex', backref='file', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'kb_id': self.kb_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat()
        }

class KBIndex(db.Model):
    __tablename__ = 'kb_indices'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('kb_files.id'), nullable=False)
    content = db.Column(db.Text)
    vector = db.Column(db.LargeBinary)
    meta_data = db.Column(db.JSON)  # 修改了这里，从metadata改为meta_data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'content': self.content[:100] + '...' if self.content and len(self.content) > 100 else self.content,
            'meta_data': self.meta_data,  # 这里也需要修改
            'created_at': self.created_at.isoformat()
        }
