// 使用React和Ant Design构建低码化工作流平台前端

const { React, ReactDOM } = window;
const { 
    Layout, Menu, Breadcrumb, Button, Card, Row, Col, 
    Form, Input, Upload, Modal, Spin, message, Tabs,
    Drawer, Select, Switch, Divider, List, Avatar
} = window.antd;
const { Header, Content, Footer, Sider } = Layout;
const { useState, useEffect } = React;
const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;

// 主应用组件
const App = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [createModalVisible, setCreateModalVisible] = useState(false);
    const [confirmLoading, setConfirmLoading] = useState(false);
    const [workflowDescription, setWorkflowDescription] = useState('');

    // 模拟获取工作流列表
    useEffect(() => {
        // 实际应用中应该从后端API获取数据
        setTimeout(() => {
            setWorkflows([
                { id: 1, name: '客户信息收集流程', description: '收集和验证客户基本信息的工作流', createdAt: '2025-03-20' },
                { id: 2, name: '产品订单处理', description: '从订单创建到发货的完整流程', createdAt: '2025-03-22' },
                { id: 3, name: '员工入职流程', description: '新员工入职文档处理和培训安排', createdAt: '2025-03-24' }
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    // 创建新工作流
    const handleCreateWorkflow = async () => {
        if (!workflowDescription.trim()) {
            message.error('请输入工作流描述');
            return;
        }

        setConfirmLoading(true);
        
        try {
            // 实际应用中应该调用后端API
            // 模拟API调用延迟
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            const newWorkflow = {
                id: workflows.length + 1,
                name: `新工作流 ${workflows.length + 1}`,
                description: workflowDescription,
                createdAt: new Date().toISOString().split('T')[0]
            };
            
            setWorkflows([...workflows, newWorkflow]);
            setCreateModalVisible(false);
            setWorkflowDescription('');
            message.success('工作流创建成功！');
        } catch (error) {
            message.error('创建工作流失败，请重试');
            console.error('创建工作流错误:', error);
        } finally {
            setConfirmLoading(false);
        }
    };

    // 渲染工作流卡片
    const renderWorkflowCards = () => {
        if (loading) {
            return (
                <div style={{ textAlign: 'center', padding: '50px' }}>
                    <Spin size="large" />
                </div>
            );
        }

        return (
            <Row gutter={[16, 16]}>
                {workflows.map(workflow => (
                    <Col xs={24} sm={12} md={8} key={workflow.id}>
                        <Card 
                            title={workflow.name}
                            className="workflow-card"
                            extra={<Button type="link">编辑</Button>}
                        >
                            <p>{workflow.description}</p>
                            <p>创建时间: {workflow.createdAt}</p>
                        </Card>
                    </Col>
                ))}
            </Row>
        );
    };

    // 渲染页面内容
    const renderContent = () => {
        switch (currentPage) {
            case 'dashboard':
                return (
                    <>
                        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                            <h2>我的工作流</h2>
                            <Button 
                                type="primary" 
                                onClick={() => setCreateModalVisible(true)}
                            >
                                创建工作流
                            </Button>
                        </div>
                        {renderWorkflowCards()}
                    </>
                );
            case 'knowledge':
                return <KnowledgeBase />;
            case 'settings':
                return <Settings />;
            default:
                return <div>页面不存在</div>;
        }
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{ background: '#fff', padding: 0, display: 'flex', alignItems: 'center' }}>
                <div className="logo" style={{ color: '#1890ff', margin: '0 24px' }}>
                    低码化工作流平台
                </div>
                <Menu theme="light" mode="horizontal" defaultSelectedKeys={['dashboard']} style={{ flex: 1 }}
                    onClick={e => setCurrentPage(e.key)}>
                    <Menu.Item key="dashboard">工作流</Menu.Item>
                    <Menu.Item key="knowledge">知识库</Menu.Item>
                    <Menu.Item key="settings">设置</Menu.Item>
                </Menu>
            </Header>
            <Content style={{ margin: '24px 16px 0' }}>
                <div className="site-layout-content">
                    {renderContent()}
                </div>
            </Content>
            <Footer style={{ textAlign: 'center' }}>低码化工作流平台 ©2025</Footer>

            {/* 创建工作流模态框 */}
            <Modal
                title="创建新工作流"
                visible={createModalVisible}
                onOk={handleCreateWorkflow}
                confirmLoading={confirmLoading}
                onCancel={() => {
                    setCreateModalVisible(false);
                    setWorkflowDescription('');
                }}
            >
                <Form layout="vertical">
                    <Form.Item label="描述您需要的工作流" required>
                        <TextArea
                            rows={6}
                            value={workflowDescription}
                            onChange={e => setWorkflowDescription(e.target.value)}
                            placeholder="请详细描述您需要的工作流，大模型将帮助您拆解和创建..."
                        />
                    </Form.Item>
                </Form>
            </Modal>
        </Layout>
    );
};

// 知识库组件
const KnowledgeBase = () => {
    const [knowledgeList, setKnowledgeList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        // 模拟从后端获取知识库列表
        setTimeout(() => {
            setKnowledgeList([
                { id: 1, name: '产品手册.pdf', size: '2.5MB', uploadTime: '2025-03-15' },
                { id: 2, name: '公司规章制度.docx', size: '1.2MB', uploadTime: '2025-03-18' },
                { id: 3, name: '客户资料.xlsx', size: '3.7MB', uploadTime: '2025-03-20' }
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const handleUpload = info => {
        if (info.file.status === 'uploading') {
            setUploading(true);
            return;
        }
        
        if (info.file.status === 'done') {
            setUploading(false);
            message.success(`${info.file.name} 上传成功`);
            // 实际应用中应该从后端获取更新后的列表
            const newFile = {
                id: knowledgeList.length + 1,
                name: info.file.name,
                size: '1.0MB',
                uploadTime: new Date().toISOString().split('T')[0]
            };
            setKnowledgeList([...knowledgeList, newFile]);
        } else if (info.file.status === 'error') {
            setUploading(false);
            message.error(`${info.file.name} 上传失败`);
        }
    };

    return (
        <div>
            <h2>知识库管理</h2>
            <p>上传文档到知识库，大模型将学习这些内容并应用到工作流创建中</p>
            
            <div className="knowledge-upload">
                <Upload
                    name="file"
                    action="/api/knowledge/upload" // 实际应用中应该指向真实的上传API
                    onChange={handleUpload}
                    showUploadList={false}
                >
                    <Button type="primary" loading={uploading}>
                        上传文档
                    </Button>
                </Upload>
            </div>
            
            <div className="knowledge-list">
                <h3>已上传文档</h3>
                {loading ? (
                    <Spin />
                ) : (
                    <List
                        bordered
                        dataSource={knowledgeList}
                        renderItem={item => (
                            <List.Item
                                actions={[
                                    <Button type="link">查看</Button>,
                                    <Button type="link" danger>删除</Button>
                                ]}
                            >
                                <List.Item.Meta
                                    title={item.name}
                                    description={`大小: ${item.size} | 上传时间: ${item.uploadTime}`}
                                />
                            </List.Item>
                        )}
                    />
                )}
            </div>
        </div>
    );
};

// 设置组件
const Settings = () => {
    const [form] = Form.useForm();
    
    useEffect(() => {
        // 模拟从后端获取设置
        form.setFieldsValue({
            apiKey: 'sk-e4193612f0da4eabbebac4388d926f99',
            dbHost: 'localhost',
            dbUser: 'root',
            dbPassword: 'admin',
            dbName: 'workflow_platform',
            port: '3000'
        });
    }, [form]);
    
    const handleSaveSettings = values => {
        console.log('保存设置:', values);
        // 实际应用中应该调用后端API保存设置
        message.success('设置已保存');
    };
    
    return (
        <div>
            <h2>系统设置</h2>
            
            <Form
                form={form}
                layout="vertical"
                onFinish={handleSaveSettings}
                style={{ maxWidth: '600px' }}
            >
                <Tabs defaultActiveKey="1">
                    <TabPane tab="大模型配置" key="1">
                        <Form.Item
                            name="apiKey"
                            label="DeepSeek API密钥"
                            rules={[{ required: true, message: '请输入API密钥' }]}
                        >
                            <Input placeholder="请输入DeepSeek API密钥" />
                        </Form.Item>
                        
                        <Form.Item name="enableAI" valuePropName="checked">
                            <Switch checkedChildren="启用" unCheckedChildren="禁用" defaultChecked /> 启用大模型功能
                        </Form.Item>
                    </TabPane>
                    
                    <TabPane tab="数据库配置" key="2">
                        <Form.Item
                            name="dbHost"
                            label="数据库主机"
                            rules={[{ required: true, message: '请输入数据库主机' }]}
                        >
                            <Input placeholder="localhost" />
                        </Form.Item>
                        
                        <Form.Item
                            name="dbUser"
                            label="数据库用户名"
                            rules={[{ required: true, message: '请输入数据库用户名' }]}
                        >
                            <Input placeholder="root" />
                        </Form.Item>
                        
                        <Form.Item
                            name="dbPassword"
                            label="数据库密码"
                            rules={[{ required: true, message: '请输入数据库密码' }]}
                        >
                            <Input.Password placeholder="请输入数据库密码" />
                        </Form.Item>
                        
                        <Form.Item
                            name="dbName"
                            label="数据库名称"
                            rules={[{ required: true, message: '请输入数据库名称' }]}
                        >
                            <Input placeholder="workflow_platform" />
                        </Form.Item>
                    </TabPane>
                    
                    <TabPane tab="服务器配置" key="3">
                        <Form.Item
                            name="port"
                            label="服务器端口"
                            rules={[{ required: true, message: '请输入服务器端口' }]}
                        >
                            <Input placeholder="3000" />
                        </Form.Item>
                    </TabPane>
                </Tabs>
                
                <Form.Item>
                    <Button type="primary" htmlType="submit">
                        保存设置
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

// 渲染应用
ReactDOM.render(<App />, document.getElementById('root'));
