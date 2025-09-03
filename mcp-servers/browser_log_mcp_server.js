#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const chokidar = require('chokidar');

class BrowserLogMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'browser-log-monitor',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.isMonitoring = false;
    this.watcher = null;
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'start_browser_log_monitor',
            description: 'Start monitoring file changes and automatically capture browser logs',
            inputSchema: {
              type: 'object',
              properties: {
                watchDirectory: {
                  type: 'string',
                  description: 'Directory to monitor for file changes',
                  default: '/home/metaspeekoj/OnlineJudgeFE/src'
                },
                targetUrl: {
                  type: 'string',
                  description: 'URL to monitor for browser logs',
                  default: 'http://localhost:8080'
                },
                fileExtensions: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'File extensions to monitor',
                  default: ['.vue', '.js', '.ts', '.css']
                }
              }
            }
          },
          {
            name: 'stop_browser_log_monitor',
            description: 'Stop the browser log monitoring',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'get_latest_browser_logs',
            description: 'Get the latest captured browser logs',
            inputSchema: {
              type: 'object',
              properties: {
                logFile: {
                  type: 'string',
                  description: 'Path to the log file',
                  default: '/home/metaspeekoj/browser_logs.txt'
                }
              }
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case 'start_browser_log_monitor':
          return this.startMonitoring(request.params.arguments);
        case 'stop_browser_log_monitor':
          return this.stopMonitoring();
        case 'get_latest_browser_logs':
          return this.getLatestLogs(request.params.arguments);
        default:
          throw new Error(`Unknown tool: ${request.params.name}`);
      }
    });
  }

  async startMonitoring(args = {}) {
    const {
      watchDirectory = '/home/metaspeekoj/OnlineJudgeFE/src',
      targetUrl = 'http://localhost:8080',
      fileExtensions = ['.vue', '.js', '.ts', '.css']
    } = args;

    if (this.isMonitoring) {
      return {
        content: [{
          type: 'text',
          text: 'Browser log monitoring is already running.'
        }]
      };
    }

    try {
      // Start file watcher
      this.watcher = chokidar.watch(watchDirectory, {
        ignored: /node_modules/,
        persistent: true
      });

      this.watcher.on('change', async (filePath) => {
        const ext = path.extname(filePath);
        if (fileExtensions.includes(ext)) {
          console.log(`File changed: ${filePath}`);
          await this.captureBrowserLogs(targetUrl, filePath);
        }
      });

      this.isMonitoring = true;

      return {
        content: [{
          type: 'text',
          text: `Browser log monitoring started.\nWatching: ${watchDirectory}\nTarget URL: ${targetUrl}\nFile extensions: ${fileExtensions.join(', ')}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Failed to start monitoring: ${error.message}`
        }]
      };
    }
  }

  async stopMonitoring() {
    if (!this.isMonitoring) {
      return {
        content: [{
          type: 'text',
          text: 'Browser log monitoring is not running.'
        }]
      };
    }

    if (this.watcher) {
      await this.watcher.close();
      this.watcher = null;
    }

    this.isMonitoring = false;

    return {
      content: [{
        type: 'text',
        text: 'Browser log monitoring stopped.'
      }]
    };
  }

  async captureBrowserLogs(targetUrl, changedFile) {
    return new Promise((resolve) => {
      const timestamp = new Date().toISOString();
      const logEntry = `\n=== Browser Log Capture ===\nTimestamp: ${timestamp}\nChanged File: ${changedFile}\nTarget URL: ${targetUrl}\n`;
      
      // Use playwright to capture browser logs
      const playwrightScript = `
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const logs = [];
  const errors = [];
  
  page.on('console', msg => {
    logs.push(\`[\${msg.type()}] \${msg.text()}\`);
  });
  
  page.on('pageerror', error => {
    errors.push(\`[ERROR] \${error.message}\`);
  });
  
  try {
    await page.goto('${targetUrl}', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    console.log('=== CONSOLE LOGS ===');
    logs.forEach(log => console.log(log));
    
    console.log('=== ERRORS ===');
    errors.forEach(error => console.log(error));
    
  } catch (error) {
    console.log('[CAPTURE ERROR]', error.message);
  } finally {
    await browser.close();
  }
})();
`;

      // Write and execute playwright script
      const scriptPath = '/tmp/capture_logs.js';
      fs.writeFileSync(scriptPath, playwrightScript);
      
      const child = spawn('node', [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      let output = '';
      child.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        output += `[STDERR] ${data.toString()}`;
      });
      
      child.on('close', (code) => {
        const fullLog = logEntry + output + '\n=== End Log Capture ===\n';
        
        // Append to log file
        fs.appendFileSync('/home/metaspeekoj/browser_logs.txt', fullLog);
        
        // Clean up temp script
        try {
          fs.unlinkSync(scriptPath);
        } catch (e) {}
        
        resolve();
      });
    });
  }

  async getLatestLogs(args = {}) {
    const { logFile = '/home/metaspeekoj/browser_logs.txt' } = args;
    
    try {
      if (!fs.existsSync(logFile)) {
        return {
          content: [{
            type: 'text',
            text: 'No browser logs found. Start monitoring first.'
          }]
        };
      }
      
      const logs = fs.readFileSync(logFile, 'utf8');
      const lines = logs.split('\n');
      const recentLines = lines.slice(-100); // Get last 100 lines
      
      return {
        content: [{
          type: 'text',
          text: `Latest browser logs:\n${recentLines.join('\n')}`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Failed to read logs: ${error.message}`
        }]
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Browser Log MCP Server running on stdio');
  }
}

const server = new BrowserLogMCPServer();
server.run().catch(console.error);