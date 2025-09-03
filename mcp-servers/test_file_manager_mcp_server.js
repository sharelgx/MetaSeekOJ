#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 测试文件管理MCP服务器
class TestFileManagerServer {
    constructor() {
        this.name = 'test-file-manager';
        this.version = '1.0.0';
        this.rootDir = '/home/metaspeekoj';
        this.testCodeDir = '/home/metaspeekoj/TestCode';
        
        // 测试文件模式
        this.testFilePatterns = [
            /^test_.*\.(py|js|html|json|txt)$/i,
            /.*_test\.(py|js|html|json|txt)$/i,
            /^.*test.*\.(py|js|html|json|txt)$/i,
            /^debug_.*\.(py|js|html|json|txt)$/i,
            /^check_.*\.(py|js|html|json|txt)$/i,
            /^assign_.*\.(py|js|html|json|txt)$/i,
            /^.*\.test\.(py|js|html|json|txt)$/i
        ];
    }

    // 确保TestCode目录存在
    ensureTestCodeDir() {
        if (!fs.existsSync(this.testCodeDir)) {
            fs.mkdirSync(this.testCodeDir, { recursive: true });
            return `创建TestCode目录: ${this.testCodeDir}`;
        }
        return `TestCode目录已存在: ${this.testCodeDir}`;
    }

    // 检测测试文件
    detectTestFiles() {
        const files = fs.readdirSync(this.rootDir);
        const testFiles = [];
        
        for (const file of files) {
            const filePath = path.join(this.rootDir, file);
            const stat = fs.statSync(filePath);
            
            // 只处理文件，跳过目录
            if (stat.isFile()) {
                // 检查是否匹配测试文件模式
                const isTestFile = this.testFilePatterns.some(pattern => pattern.test(file));
                if (isTestFile) {
                    testFiles.push({
                        name: file,
                        path: filePath,
                        size: stat.size,
                        modified: stat.mtime.toISOString()
                    });
                }
            }
        }
        
        return testFiles;
    }

    // 移动测试文件
    moveTestFiles(files = null) {
        this.ensureTestCodeDir();
        
        const testFiles = files || this.detectTestFiles();
        const results = [];
        
        for (const file of testFiles) {
            try {
                const sourcePath = typeof file === 'string' ? path.join(this.rootDir, file) : file.path;
                const fileName = typeof file === 'string' ? file : file.name;
                const targetPath = path.join(this.testCodeDir, fileName);
                
                // 检查源文件是否存在
                if (!fs.existsSync(sourcePath)) {
                    results.push({
                        file: fileName,
                        status: 'error',
                        message: '源文件不存在'
                    });
                    continue;
                }
                
                // 如果目标文件已存在，创建备份
                if (fs.existsSync(targetPath)) {
                    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                    const backupPath = path.join(this.testCodeDir, `${fileName}.backup.${timestamp}`);
                    fs.renameSync(targetPath, backupPath);
                    results.push({
                        file: fileName,
                        status: 'backup',
                        message: `已备份现有文件为: ${path.basename(backupPath)}`
                    });
                }
                
                // 移动文件
                fs.renameSync(sourcePath, targetPath);
                results.push({
                    file: fileName,
                    status: 'moved',
                    message: `已移动到: ${targetPath}`
                });
                
            } catch (error) {
                results.push({
                    file: typeof file === 'string' ? file : file.name,
                    status: 'error',
                    message: error.message
                });
            }
        }
        
        return results;
    }

    // 获取TestCode目录状态
    getTestCodeStatus() {
        if (!fs.existsSync(this.testCodeDir)) {
            return {
                exists: false,
                files: [],
                totalFiles: 0,
                totalSize: 0
            };
        }
        
        const files = fs.readdirSync(this.testCodeDir);
        const fileDetails = [];
        let totalSize = 0;
        
        for (const file of files) {
            const filePath = path.join(this.testCodeDir, file);
            const stat = fs.statSync(filePath);
            
            if (stat.isFile()) {
                const fileInfo = {
                    name: file,
                    size: stat.size,
                    modified: stat.mtime.toISOString()
                };
                fileDetails.push(fileInfo);
                totalSize += stat.size;
            }
        }
        
        return {
            exists: true,
            path: this.testCodeDir,
            files: fileDetails,
            totalFiles: fileDetails.length,
            totalSize: totalSize
        };
    }

    // 清理根目录测试文件
    cleanRootTestFiles() {
        const testFiles = this.detectTestFiles();
        if (testFiles.length === 0) {
            return {
                message: '根目录下没有检测到测试文件',
                moved: []
            };
        }
        
        const results = this.moveTestFiles(testFiles);
        const movedFiles = results.filter(r => r.status === 'moved');
        
        return {
            message: `检测到 ${testFiles.length} 个测试文件，成功移动 ${movedFiles.length} 个`,
            moved: results
        };
    }

    // 创建测试文件（直接在TestCode目录中）
    createTestFile(fileName, content = '', fileType = 'py') {
        this.ensureTestCodeDir();
        
        // 确保文件名符合测试文件命名规范
        if (!fileName.startsWith('test_') && !fileName.endsWith('_test')) {
            fileName = `test_${fileName}`;
        }
        
        // 确保有正确的文件扩展名
        if (!fileName.includes('.')) {
            fileName += `.${fileType}`;
        }
        
        const filePath = path.join(this.testCodeDir, fileName);
        
        try {
            // 检查文件是否已存在
            if (fs.existsSync(filePath)) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const backupPath = path.join(this.testCodeDir, `${fileName}.backup.${timestamp}`);
                fs.renameSync(filePath, backupPath);
            }
            
            // 创建文件
            fs.writeFileSync(filePath, content, 'utf8');
            
            return {
                success: true,
                fileName: fileName,
                filePath: filePath,
                message: `测试文件已创建: ${fileName}`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                message: `创建测试文件失败: ${error.message}`
            };
        }
    }

    // 处理MCP请求
    handleRequest(method, params = {}) {
        try {
            switch (method) {
                case 'detect_test_files':
                    const testFiles = this.detectTestFiles();
                    return {
                        success: true,
                        data: {
                            message: `检测到 ${testFiles.length} 个测试文件`,
                            files: testFiles
                        }
                    };
                
                case 'move_test_files':
                    const moveResults = this.moveTestFiles(params.files);
                    return {
                        success: true,
                        data: {
                            message: `文件移动操作完成`,
                            results: moveResults
                        }
                    };
                
                case 'get_testcode_status':
                    const status = this.getTestCodeStatus();
                    return {
                        success: true,
                        data: status
                    };
                
                case 'clean_root_test_files':
                    const cleanResults = this.cleanRootTestFiles();
                    return {
                        success: true,
                        data: cleanResults
                    };
                
                case 'ensure_testcode_dir':
                    const dirResult = this.ensureTestCodeDir();
                    return {
                        success: true,
                        data: {
                            message: dirResult,
                            path: this.testCodeDir
                        }
                    };
                
                case 'create_test_file':
                    const createResult = this.createTestFile(
                        params.fileName || 'new_test',
                        params.content || '',
                        params.fileType || 'py'
                    );
                    return {
                        success: createResult.success,
                        data: createResult.success ? {
                            message: createResult.message,
                            fileName: createResult.fileName,
                            filePath: createResult.filePath
                        } : null,
                        error: createResult.success ? null : createResult.error
                    };
                
                default:
                    return {
                        success: false,
                        error: `未知方法: ${method}`
                    };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// MCP协议处理
class MCPServer {
    constructor() {
        this.testManager = new TestFileManagerServer();
        this.tools = [
            {
                name: 'detect_test_files',
                description: '检测根目录下的测试文件',
                inputSchema: {
                    type: 'object',
                    properties: {},
                    required: []
                }
            },
            {
                name: 'move_test_files',
                description: '移动测试文件到TestCode目录',
                inputSchema: {
                    type: 'object',
                    properties: {
                        files: {
                            type: 'array',
                            description: '要移动的文件列表（可选，不提供则移动所有检测到的测试文件）',
                            items: { type: 'string' }
                        }
                    },
                    required: []
                }
            },
            {
                name: 'get_testcode_status',
                description: '获取TestCode目录状态和文件列表',
                inputSchema: {
                    type: 'object',
                    properties: {},
                    required: []
                }
            },
            {
                name: 'clean_root_test_files',
                description: '清理根目录下的所有测试文件，移动到TestCode目录',
                inputSchema: {
                    type: 'object',
                    properties: {},
                    required: []
                }
            },
            {
                name: 'ensure_testcode_dir',
                description: '确保TestCode目录存在',
                inputSchema: {
                    type: 'object',
                    properties: {},
                    required: []
                }
            },
            {
                name: 'create_test_file',
                description: '在TestCode目录中创建新的测试文件',
                inputSchema: {
                    type: 'object',
                    properties: {
                        fileName: {
                            type: 'string',
                            description: '测试文件名（会自动添加test_前缀如果没有的话）'
                        },
                        content: {
                            type: 'string',
                            description: '文件内容（可选）',
                            default: ''
                        },
                        fileType: {
                            type: 'string',
                            description: '文件类型扩展名（py, js, html等）',
                            default: 'py'
                        }
                    },
                    required: ['fileName']
                }
            }
        ];
    }

    async handleToolCall(name, args) {
        const result = this.testManager.handleRequest(name, args);
        
        if (result.success) {
            return [{
                type: 'text',
                text: this.formatResponse(name, result.data)
            }];
        } else {
            throw new Error(result.error);
        }
    }

    formatResponse(method, data) {
        switch (method) {
            case 'detect_test_files':
                if (data.files.length === 0) {
                    return '=== 测试文件检测结果 ===\n未在根目录检测到测试文件';
                }
                
                let output = `=== 测试文件检测结果 ===\n检测到 ${data.files.length} 个测试文件:\n\n`;
                data.files.forEach(file => {
                    output += `📄 ${file.name}\n   大小: ${(file.size / 1024).toFixed(2)} KB\n   修改时间: ${new Date(file.modified).toLocaleString()}\n\n`;
                });
                return output;
            
            case 'move_test_files':
                let moveOutput = '=== 测试文件移动结果 ===\n';
                data.results.forEach(result => {
                    const icon = result.status === 'moved' ? '✅' : result.status === 'backup' ? '🔄' : '❌';
                    moveOutput += `${icon} ${result.file}: ${result.message}\n`;
                });
                return moveOutput;
            
            case 'get_testcode_status':
                if (!data.exists) {
                    return '=== TestCode目录状态 ===\nTestCode目录不存在';
                }
                
                let statusOutput = `=== TestCode目录状态 ===\n路径: ${data.path}\n文件数量: ${data.totalFiles}\n总大小: ${(data.totalSize / 1024).toFixed(2)} KB\n\n`;
                
                if (data.files.length > 0) {
                    statusOutput += '文件列表:\n';
                    data.files.forEach(file => {
                        statusOutput += `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)\n`;
                    });
                } else {
                    statusOutput += '目录为空';
                }
                
                return statusOutput;
            
            case 'clean_root_test_files':
                let cleanOutput = `=== 根目录测试文件清理 ===\n${data.message}\n\n`;
                if (data.moved.length > 0) {
                    cleanOutput += '移动详情:\n';
                    data.moved.forEach(result => {
                        const icon = result.status === 'moved' ? '✅' : result.status === 'backup' ? '🔄' : '❌';
                        cleanOutput += `${icon} ${result.file}: ${result.message}\n`;
                    });
                }
                return cleanOutput;
            
            case 'ensure_testcode_dir':
                return `=== TestCode目录管理 ===\n${data.message}\n路径: ${data.path}`;
            
            case 'create_test_file':
                return `=== 测试文件创建 ===\n✅ ${data.message}\n文件名: ${data.fileName}\n路径: ${data.filePath}`;
            
            default:
                return JSON.stringify(data, null, 2);
        }
    }

    async run() {
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        // 发送初始化响应
        console.log(JSON.stringify({
            jsonrpc: '2.0',
            result: {
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: {
                        listChanged: true
                    }
                },
                serverInfo: {
                    name: 'test-file-manager',
                    version: '1.0.0'
                }
            }
        }));

        // 立即发送工具列表
        console.log(JSON.stringify({
            jsonrpc: '2.0',
            method: 'notifications/tools/list_changed',
            params: {}
        }));

        // 处理输入
        rl.on('line', async (line) => {
            try {
                const request = JSON.parse(line);
                
                if (request.method === 'tools/list') {
                    console.log(JSON.stringify({
                        jsonrpc: '2.0',
                        id: request.id,
                        result: {
                            tools: this.tools
                        }
                    }));
                } else if (request.method === 'tools/call') {
                    const { name, arguments: args } = request.params;
                    const result = await this.handleToolCall(name, args || {});
                    
                    console.log(JSON.stringify({
                        jsonrpc: '2.0',
                        id: request.id,
                        result: {
                            content: result
                        }
                    }));
                }
            } catch (error) {
                console.log(JSON.stringify({
                    jsonrpc: '2.0',
                    id: request?.id,
                    error: {
                        code: -1,
                        message: error.message
                    }
                }));
            }
        });
    }
}

// 启动服务器
if (require.main === module) {
    const server = new MCPServer();
    server.run().catch(console.error);
}

module.exports = { TestFileManagerServer, MCPServer };