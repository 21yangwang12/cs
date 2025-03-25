const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const mysql = require('mysql2/promise');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

// 初始化Express应用
const app = express();
const port = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../frontend')));

// 文件上传配置
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

// 数据库连接配置
let dbConfig = {
  host: 'localhost',
  user: 'root',
  password: 'admin',
  database: 'workflow_platform'
};

// 创建数据库连接池
const pool = mysql.createPool(dbConfig);

// 测试数据库连接
async function testDbConnection() {
  try {
    const connection = await pool.getConnection();
    console.log('数据库连接成功');
    connection.release();
    return true;
  } catch (error) {
    console.error('数据库连接失败:', error);
    return false;
  }
}

// DeepSeek API配置
let deepseekApiKey = 'sk-e4193612f0da4eabbebac4388d926f99';

// API路由

// 获取所有工作流
app.get('/api/workflows', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM workflows ORDER BY created_at DESC');
    res.json(rows);
  } catch (error) {
    console.error('获取工作流失败:', error);
    res.status(500).json({ error: '获取工作流失败' });
  }
});

// 获取单个工作流
app.get('/api/workflows/:id', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM workflows WHERE id = ?', [req.params.id]);
    if (rows.length === 0) {
      return res.status(404).json({ error: '工作流不存在' });
    }
    res.json(rows[0]);
  } catch (error) {
    console.error('获取工作流失败:', error);
    res.status(500).json({ error: '获取工作流失败' });
  }
});

// 创建工作流
app.post('/api/workflows', async (req, res) => {
  const { name, description } = req.body;
  
  if (!description) {
    return res.status(400).json({ error: '工作流描述不能为空' });
  }
  
  try {
    // 调用DeepSeek API解析工作流
    const workflowSteps = await parseWorkflowWithAI(description);
    
    // 将工作流保存到数据库
    const [result] = await pool.query(
      'INSERT INTO workflows (name, description, steps, created_at) VALUES (?, ?, ?, NOW())',
      [name || `新工作流 ${Date.now()}`, description, JSON.stringify(workflowSteps)]
    );
    
    const workflowId = result.insertId;
    
    // 获取新创建的工作流
    const [rows] = await pool.query('SELECT * FROM workflows WHERE id = ?', [workflowId]);
    
    res.status(201).json(rows[0]);
  } catch (error) {
    console.error('创建工作流失败:', error);
    res.status(500).json({ error: '创建工作流失败' });
  }
});

// 更新工作流
app.put('/api/workflows/:id', async (req, res) => {
  const { name, description, steps } = req.body;
  
  try {
    await pool.query(
      'UPDATE workflows SET name = ?, description = ?, steps = ?, updated_at = NOW() WHERE id = ?',
      [name, description, JSON.stringify(steps), req.params.id]
    );
    
    const [rows] = await pool.query('SELECT * FROM workflows WHERE id = ?', [req.params.id]);
    
    if (rows.length === 0) {
      return res.status(404).json({ error: '工作流不存在' });
    }
    
    res.json(rows[0]);
  } catch (error) {
    console.error('更新工作流失败:', error);
    res.status(500).json({ error: '更新工作流失败' });
  }
});

// 删除工作流
app.delete('/api/workflows/:id', async (req, res) => {
  try {
    const [result] = await pool.query('DELETE FROM workflows WHERE id = ?', [req.params.id]);
    
    if (result.affectedRows === 0) {
      return res.status(404).json({ error: '工作流不存在' });
    }
    
    res.json({ message: '工作流已删除' });
  } catch (error) {
    console.error('删除工作流失败:', error);
    res.status(500).json({ error: '删除工作流失败' });
  }
});

// 上传知识库文件
app.post('/api/knowledge/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: '未提供文件' });
  }
  
  try {
    const { filename, originalname, size, path: filePath } = req.file;
    
    // 将文件信息保存到数据库
    const [result] = await pool.query(
      'INSERT INTO knowledge_files (name, filename, size, path, uploaded_at) VALUES (?, ?, ?, ?, NOW())',
      [originalname, filename, size, filePath]
    );
    
    res.status(201).json({
      id: result.insertId,
      name: originalname,
      size,
      uploadTime: new Date().toISOString()
    });
  } catch (error) {
    console.error('上传文件失败:', error);
    res.status(500).json({ error: '上传文件失败' });
  }
});

// 获取知识库文件列表
app.get('/api/knowledge', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM knowledge_files ORDER BY uploaded_at DESC');
    
    const files = rows.map(file => ({
      id: file.id,
      name: file.name,
      size: formatFileSize(file.size),
      uploadTime: new Date(file.uploaded_at).toISOString().split('T')[0]
    }));
    
    res.json(files);
  } catch (error) {
    console.error('获取知识库文件失败:', error);
    res.status(500).json({ error: '获取知识库文件失败' });
  }
});

// 删除知识库文件
app.delete('/api/knowledge/:id', async (req, res) => {
  try {
    // 获取文件信息
    const [files] = await pool.query('SELECT * FROM knowledge_files WHERE id = ?', [req.params.id]);
    
    if (files.length === 0) {
      return res.status(404).json({ error: '文件不存在' });
    }
    
    const file = files[0];
    
    // 删除物理文件
    fs.unlinkSync(file.path);
    
    // 从数据库中删除记录
    await pool.query('DELETE FROM knowledge_files WHERE id = ?', [req.params.id]);
    
    res.json({ message: '文件已删除' });
  } catch (error) {
    console.error('删除文件失败:', error);
    res.status(500).json({ error: '删除文件失败' });
  }
});

// 获取系统设置
app.get('/api/settings', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM settings');
    
    const settings = rows.reduce((acc, setting) => {
      acc[setting.key] = setting.value;
      return acc;
    }, {});
    
    res.json(settings);
  } catch (error) {
    console.error('获取设置失败:', error);
    res.status(500).json({ error: '获取设置失败' });
  }
});

// 更新系统设置
app.put('/api/settings', async (req, res) => {
  const settings = req.body;
  
  try {
    // 更新数据库连接配置
    if (settings.dbHost && settings.dbUser && settings.dbPassword && settings.dbName) {
      dbConfig = {
        host: settings.dbHost,
        user: settings.dbUser,
        password: settings.dbPassword,
        database: settings.dbName
      };
      
      // 重新创建连接池
      pool.end();
      pool = mysql.createPool(dbConfig);
      
      // 测试新连接
      const connected = await testDbConnection();
      if (!connected) {
        return res.status(500).json({ error: '数据库连接失败，请检查配置' });
      }
    }
    
    // 更新DeepSeek API密钥
    if (settings.apiKey) {
      deepseekApiKey = settings.apiKey;
    }
    
    // 更新设置到数据库
    for (const [key, value] of Object.entries(settings)) {
      await pool.query(
        'INSERT INTO settings (key, value) VALUES (?, ?) ON DUPLICATE KEY UPDATE value = ?',
        [key, value, value]
      );
    }
    
    res.json({ message: '设置已更新' });
  } catch (error) {
    console.error('更新设置失败:', error);
    res.status(500).json({ error: '更新设置失败' });
  }
});

// 辅助函数

// 使用DeepSeek API解析工作流
async function parseWorkflowWithAI(description) {
  try {
    const response = await axios.post(
      'https://api.deepseek.com/v1/chat/completions',
      {
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一个工作流解析助手，可以将用户描述的工作流拆解为具体步骤。'
          },
          {
            role: 'user',
            content: `请将以下工作流描述拆解为具体步骤，以JSON格式返回，包含步骤名称、描述、类型和所需输入：\n\n${description}`
          }
        ],
        temperature: 0.7
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${deepseekApiKey}`
        }
      }
    );
    
    const aiResponse = response.data.choices[0].message.content;
    
    // 提取JSON部分
    const jsonMatch = aiResponse.match(/```json([\s\S]*?)```/) || aiResponse.match(/{[\s\S]*}/);
    const jsonString = jsonMatch ? (jsonMatch[1] || jsonMatch[0]) : '[]';
    
    try {
      return JSON.parse(jsonString);
    } catch (e) {
      console.error('解析AI返回的JSON失败:', e);
      return [];
    }
  } catch (error) {
    console.error('调用DeepSeek API失败:', error);
    return [];
  }
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// 启动服务器
app.listen(port, '0.0.0.0', async () => {
  console.log(`服务器运行在 http://0.0.0.0:${port}`);
  
  // 测试数据库连接
  await testDbConnection();
});

// 处理未捕获的异常
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常:', error);
});

process.on('unhandledRejection', (error) => {
  console.error('未处理的Promise拒绝:', error);
});
