# 低码化工作流平台部署指南

本文档提供了低码化工作流平台的部署步骤和配置说明。

## 系统要求

- Node.js 14.x 或更高版本
- MySQL 5.7 或更高版本
- 现代浏览器（Chrome、Firefox、Edge等）

## 部署步骤

### 1. 数据库配置

1. 登录MySQL：
   ```bash
   mysql -u root -p
   ```

2. 执行初始化脚本：
   ```bash
   mysql -u root -p < /path/to/workflow-platform/database/init.sql
   ```
   或者在MySQL客户端中执行：
   ```sql
   source /path/to/workflow-platform/database/init.sql
   ```

### 2. 后端服务配置

1. 安装依赖：
   ```bash
   cd /path/to/workflow-platform/backend
   npm install express body-parser cors mysql2 multer axios
   ```

2. 配置环境变量（可选）：
   创建`.env`文件：
   ```
   PORT=3000
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=admin
   DB_NAME=workflow_platform
   DEEPSEEK_API_KEY=sk-e4193612f0da4eabbebac4388d926f99
   ```

3. 启动后端服务：
   ```bash
   node server.js
   ```

### 3. 前端配置

前端文件已经配置为静态资源，由后端服务直接提供。无需额外的构建步骤。

## 访问平台

启动服务后，通过浏览器访问：
```
http://localhost:3000
```

## 配置说明

### 数据库配置

默认数据库配置：
- 主机：localhost
- 用户名：root
- 密码：admin
- 数据库名：workflow_platform

可以在平台的"设置"页面中修改这些配置。

### DeepSeek API配置

平台使用DeepSeek API进行工作流解析。默认API密钥已配置，但建议替换为您自己的API密钥：
- API密钥：sk-e4193612f0da4eabbebac4388d926f99

可以在平台的"设置"页面中更新API密钥。

## 知识库管理

平台支持上传文档到知识库，这些文档将被用于工作流创建过程中。支持的文件格式包括：
- PDF
- Word文档
- Excel表格
- 文本文件

上传的文件将保存在`/path/to/workflow-platform/backend/uploads`目录中。

## 故障排除

### 数据库连接问题

如果遇到数据库连接问题，请检查：
1. MySQL服务是否正在运行
2. 数据库凭证是否正确
3. 数据库是否已创建

### API调用失败

如果DeepSeek API调用失败，请检查：
1. API密钥是否有效
2. 网络连接是否正常
3. API服务是否可用

## 生产环境部署

对于生产环境，建议：
1. 使用PM2等工具管理Node.js进程
2. 配置Nginx作为反向代理
3. 启用HTTPS
4. 实施适当的安全措施（防火墙、认证等）

示例PM2配置：
```json
{
  "apps": [{
    "name": "workflow-platform",
    "script": "server.js",
    "cwd": "/path/to/workflow-platform/backend",
    "instances": "max",
    "exec_mode": "cluster",
    "env": {
      "NODE_ENV": "production",
      "PORT": 3000
    }
  }]
}
```

示例Nginx配置：
```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```
