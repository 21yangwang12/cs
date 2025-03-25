-- 初始化数据库脚本
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS workflow_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE workflow_platform;

-- 创建工作流表
CREATE TABLE IF NOT EXISTS workflows (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  steps JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建知识库文件表
CREATE TABLE IF NOT EXISTS knowledge_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  filename VARCHAR(255) NOT NULL,
  size BIGINT NOT NULL,
  path VARCHAR(512) NOT NULL,
  content_type VARCHAR(100),
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建设置表
CREATE TABLE IF NOT EXISTS settings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `key` VARCHAR(100) NOT NULL UNIQUE,
  value TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认设置
INSERT INTO settings (`key`, value) VALUES
('apiKey', 'sk-e4193612f0da4eabbebac4388d926f99'),
('dbHost', 'localhost'),
('dbUser', 'root'),
('dbPassword', 'admin'),
('dbName', 'workflow_platform'),
('port', '3000'),
('enableAI', 'true');

-- 插入示例工作流
INSERT INTO workflows (name, description, steps) VALUES
('客户信息收集流程', '收集和验证客户基本信息的工作流', '[
  {"name": "信息收集", "description": "收集客户基本信息", "type": "form", "inputs": ["姓名", "电话", "邮箱", "地址"]},
  {"name": "信息验证", "description": "验证客户提供的信息", "type": "validation", "inputs": ["电话验证", "邮箱验证"]},
  {"name": "数据存储", "description": "将验证后的信息存入数据库", "type": "database", "inputs": ["客户信息"]}
]'),
('产品订单处理', '从订单创建到发货的完整流程', '[
  {"name": "订单创建", "description": "创建新订单", "type": "form", "inputs": ["产品", "数量", "客户信息"]},
  {"name": "库存检查", "description": "检查产品库存", "type": "service", "inputs": ["产品ID", "数量"]},
  {"name": "支付处理", "description": "处理订单支付", "type": "payment", "inputs": ["订单ID", "支付方式"]},
  {"name": "订单确认", "description": "确认订单并准备发货", "type": "notification", "inputs": ["订单ID"]},
  {"name": "物流安排", "description": "安排物流发货", "type": "service", "inputs": ["订单ID", "物流方式"]}
]'),
('员工入职流程', '新员工入职文档处理和培训安排', '[
  {"name": "资料收集", "description": "收集新员工个人资料", "type": "form", "inputs": ["个人信息", "证件照", "学历证明"]},
  {"name": "合同准备", "description": "准备劳动合同", "type": "document", "inputs": ["员工信息", "岗位信息", "薪资信息"]},
  {"name": "账号创建", "description": "创建公司内部账号", "type": "service", "inputs": ["员工ID", "部门", "职位"]},
  {"name": "培训安排", "description": "安排入职培训", "type": "calendar", "inputs": ["员工ID", "培训课程", "培训时间"]},
  {"name": "设备分配", "description": "分配办公设备", "type": "inventory", "inputs": ["员工ID", "设备类型", "设备数量"]}
]');
