#!/usr/bin/env node

/**
 * Git推送MCP服务器
 * 提供完整的Git推送功能，包括添加、提交、推送等操作
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

const execAsync = promisify(exec);

class GitPushServer {
    constructor() {
        this.rootDir = '/home/metaspeekoj';
        this.server = new Server(
            {
                name: 'git-push-server',
                version: '1.0.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        this.setupToolHandlers();
        this.setupErrorHandling();
    }

    setupErrorHandling() {
        this.server.onerror = (error) => {
            console.error('[MCP Error]', error);
        };

        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }

    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    {
                        name: 'git_push_all',
                        description: '推送所有修改到GitHub，包括添加、提交和推送操作',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                commit_message: {
                                    type: 'string',
                                    description: '提交信息',
                                    default: '自动提交：更新项目文件'
                                },
                                add_tag: {
                                    type: 'boolean',
                                    description: '是否添加标签',
                                    default: false
                                },
                                tag_name: {
                                    type: 'string',
                                    description: '标签名称（如果add_tag为true）'
                                },
                                tag_message: {
                                    type: 'string',
                                    description: '标签信息（如果add_tag为true）'
                                }
                            },
                            required: []
                        }
                    },
                    {
                        name: 'git_status',
                        description: '检查Git仓库状态',
                        inputSchema: {
                            type: 'object',
                            properties: {},
                            required: []
                        }
                    },
                    {
                        name: 'git_add_commit',
                        description: '添加文件到暂存区并提交',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                files: {
                                    type: 'array',
                                    description: '要添加的文件列表，默认为所有文件(.)',
                                    items: { type: 'string' },
                                    default: ['.']
                                },
                                commit_message: {
                                    type: 'string',
                                    description: '提交信息',
                                    default: '自动提交：更新项目文件'
                                }
                            },
                            required: []
                        }
                    },
                    {
                        name: 'git_push',
                        description: '推送到远程仓库',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                remote: {
                                    type: 'string',
                                    description: '远程仓库名称',
                                    default: 'origin'
                                },
                                branch: {
                                    type: 'string',
                                    description: '分支名称',
                                    default: 'main'
                                },
                                push_tags: {
                                    type: 'boolean',
                                    description: '是否推送标签',
                                    default: false
                                }
                            },
                            required: []
                        }
                    }
                ]
            };
        });

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case 'git_push_all':
                        return await this.gitPushAll(args);
                    case 'git_status':
                        return await this.gitStatus();
                    case 'git_add_commit':
                        return await this.gitAddCommit(args);
                    case 'git_push':
                        return await this.gitPush(args);
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `错误: ${error.message}`
                        }
                    ],
                    isError: true
                };
            }
        });
    }

    async executeCommand(command, cwd = this.rootDir) {
        try {
            const { stdout, stderr } = await execAsync(command, { cwd });
            return {
                success: true,
                stdout: stdout.trim(),
                stderr: stderr.trim()
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                stdout: error.stdout || '',
                stderr: error.stderr || ''
            };
        }
    }

    async gitStatus() {
        const result = await this.executeCommand('git status --porcelain');
        const statusResult = await this.executeCommand('git status');
        
        return {
            content: [
                {
                    type: 'text',
                    text: `Git仓库状态:\n\n${statusResult.stdout}\n\n修改的文件:\n${result.stdout || '没有修改的文件'}`
                }
            ]
        };
    }

    async gitAddCommit(args = {}) {
        const files = args.files || ['.'];
        const commitMessage = args.commit_message || '自动提交：更新项目文件';
        
        let results = [];
        
        // 添加文件
        const addCommand = `git add ${files.join(' ')}`;
        const addResult = await this.executeCommand(addCommand);
        
        if (!addResult.success) {
            throw new Error(`添加文件失败: ${addResult.error}`);
        }
        
        results.push(`✅ 文件添加成功: ${files.join(', ')}`);
        
        // 提交
        const commitCommand = `git commit -m "${commitMessage}"`;
        const commitResult = await this.executeCommand(commitCommand);
        
        if (!commitResult.success) {
            if (commitResult.stderr.includes('nothing to commit')) {
                results.push('ℹ️ 没有需要提交的更改');
            } else {
                throw new Error(`提交失败: ${commitResult.error}`);
            }
        } else {
            results.push(`✅ 提交成功: ${commitMessage}`);
            results.push(`提交详情:\n${commitResult.stdout}`);
        }
        
        return {
            content: [
                {
                    type: 'text',
                    text: results.join('\n\n')
                }
            ]
        };
    }

    async gitPush(args = {}) {
        const remote = args.remote || 'origin';
        const branch = args.branch || 'main';
        const pushTags = args.push_tags || false;
        
        let results = [];
        
        // 推送代码
        const pushCommand = `git push ${remote} ${branch}`;
        const pushResult = await this.executeCommand(pushCommand);
        
        if (!pushResult.success) {
            throw new Error(`推送失败: ${pushResult.error}\n${pushResult.stderr}`);
        }
        
        results.push(`✅ 代码推送成功到 ${remote}/${branch}`);
        results.push(`推送详情:\n${pushResult.stdout || pushResult.stderr}`);
        
        // 推送标签（如果需要）
        if (pushTags) {
            const pushTagsCommand = `git push ${remote} --tags`;
            const pushTagsResult = await this.executeCommand(pushTagsCommand);
            
            if (pushTagsResult.success) {
                results.push(`✅ 标签推送成功`);
            } else {
                results.push(`⚠️ 标签推送失败: ${pushTagsResult.error}`);
            }
        }
        
        return {
            content: [
                {
                    type: 'text',
                    text: results.join('\n\n')
                }
            ]
        };
    }

    async gitPushAll(args = {}) {
        const commitMessage = args.commit_message || '自动提交：更新项目文件';
        const addTag = args.add_tag || false;
        const tagName = args.tag_name;
        const tagMessage = args.tag_message;
        
        let results = [];
        
        try {
            // 1. 检查状态
            results.push('🔍 检查Git状态...');
            const statusResult = await this.executeCommand('git status --porcelain');
            
            if (!statusResult.stdout.trim()) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: 'ℹ️ 没有需要推送的更改，仓库已是最新状态。'
                        }
                    ]
                };
            }
            
            // 2. 添加所有文件
            results.push('📁 添加所有修改的文件...');
            const addResult = await this.executeCommand('git add .');
            if (!addResult.success) {
                throw new Error(`添加文件失败: ${addResult.error}`);
            }
            
            // 3. 提交
            results.push('💾 提交更改...');
            const commitResult = await this.executeCommand(`git commit -m "${commitMessage}"`);
            if (!commitResult.success && !commitResult.stderr.includes('nothing to commit')) {
                throw new Error(`提交失败: ${commitResult.error}`);
            }
            
            if (commitResult.success) {
                results.push(`✅ 提交成功: ${commitMessage}`);
            }
            
            // 4. 添加标签（如果需要）
            if (addTag && tagName) {
                results.push('🏷️ 添加标签...');
                const tagCommand = tagMessage ? 
                    `git tag -a ${tagName} -m "${tagMessage}"` : 
                    `git tag ${tagName}`;
                const tagResult = await this.executeCommand(tagCommand);
                if (tagResult.success) {
                    results.push(`✅ 标签添加成功: ${tagName}`);
                } else {
                    results.push(`⚠️ 标签添加失败: ${tagResult.error}`);
                }
            }
            
            // 5. 推送到远程仓库
            results.push('🚀 推送到GitHub...');
            const pushResult = await this.executeCommand('git push origin main');
            if (!pushResult.success) {
                throw new Error(`推送失败: ${pushResult.error}\n${pushResult.stderr}`);
            }
            
            results.push('✅ 代码推送成功!');
            
            // 6. 推送标签（如果有）
            if (addTag && tagName) {
                results.push('🏷️ 推送标签...');
                const pushTagsResult = await this.executeCommand('git push origin --tags');
                if (pushTagsResult.success) {
                    results.push('✅ 标签推送成功!');
                } else {
                    results.push(`⚠️ 标签推送失败: ${pushTagsResult.error}`);
                }
            }
            
            // 7. 显示最终状态
            const finalStatusResult = await this.executeCommand('git log --oneline -3');
            if (finalStatusResult.success) {
                results.push(`\n📋 最近的提交:\n${finalStatusResult.stdout}`);
            }
            
            return {
                content: [
                    {
                        type: 'text',
                        text: results.join('\n')
                    }
                ]
            };
            
        } catch (error) {
            results.push(`❌ 操作失败: ${error.message}`);
            return {
                content: [
                    {
                        type: 'text',
                        text: results.join('\n')
                    }
                ],
                isError: true
            };
        }
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Git推送MCP服务器已启动');
    }
}

const server = new GitPushServer();
server.run().catch(console.error);