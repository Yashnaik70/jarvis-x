from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .api.routes import router

app = FastAPI(title="JARVIS-X Backend", description="Personal AI assistant core services.")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    app.state.ready = True

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>JARVIS-X Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #0a0f1d; color: #e6eef8; }
            header { background: #121b33; padding: 24px; text-align: center; }
            h1 { margin: 0; font-size: 2rem; }
            main { padding: 24px; }
            .card { background: #16203d; border-radius: 14px; padding: 18px; margin-bottom: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
            .card h2 { margin-top: 0; }
            .button { background: #3f80ff; border: none; color: white; padding: 12px 16px; border-radius: 8px; cursor: pointer; }
            .button:hover { background: #5a9dff; }
            pre { background: #0f1730; padding: 12px; border-radius: 8px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <header>
            <h1>JARVIS-X Dashboard</h1>
            <p>Personal AI assistant control panel</p>
        </header>
        <main>
            <div class="card">
                <h2>System overview</h2>
                <button class="button" onclick="loadOverview()">Refresh status</button>
                <pre id="overview">Loading...</pre>
            </div>
            <div class="card">
                <h2>Voice subsystem</h2>
                <button class="button" onclick="loadVoice()">Load voice status</button>
                <pre id="voice">Press the button to check voice status.</pre>
            </div>
            <div class="card">
                <h2>Voice STT / TTS</h2>
                <input id="ttsText" type="text" placeholder="Text to speak" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-bottom: 10px;" />
                <button class="button" onclick="generateSpeech()">Generate speech</button>
                <pre id="ttsResult">Enter text and click Generate speech.</pre>
                <input id="sttFile" type="file" accept="audio/wav" style="width: 100%; margin-top: 10px;" />
                <button class="button" onclick="transcribeAudio()" style="margin-top: 10px;">Transcribe WAV</button>
                <pre id="sttResult">Upload a WAV file and click Transcribe WAV.</pre>
            </div>
            <div class="card">
                <h2>Memory search</h2>
                <input id="memoryQuery" type="text" placeholder="Search memory" style="width: calc(100% - 122px); padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                <button class="button" onclick="searchMemory()" style="margin-top: 10px;">Search</button>
                <pre id="memorySearch">Enter a search term and press Search.</pre>
            </div>
            <div class="card">
                <h2>Tools</h2>
                <button class="button" onclick="loadTools()">Load tools</button>
                <pre id="tools">Press the button to list available tools.</pre>
            </div>
            <div class="card">
                <h2>Web search</h2>
                <input id="webSearchQuery" type="text" placeholder="Search the web" style="width: calc(100% - 122px); padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                <button class="button" onclick="executeWebSearch()" style="margin-top: 10px;">Search</button>
                <pre id="webSearchResult">Enter a query and click Search to use the SerpAPI web search tool.</pre>
            </div>
            <div class="card">
                <h2>Tool executor</h2>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <input id="toolName" type="text" placeholder="Tool name" style="flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                    <input id="toolParams" type="text" placeholder='JSON params e.g. {"path":"."}' style="flex: 2; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                </div>
                <button class="button" onclick="executeTool()" style="margin-top: 10px;">Execute tool</button>
                <pre id="toolResult">Enter a tool name and parameters, then click Execute.</pre>
            </div>
            <div class="card">
                <h2>Automation workflows</h2>
                <button class="button" onclick="loadWorkflows()">List workflows</button>
                <pre id="workflows">Press the button to list available workflows.</pre>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                    <input id="workflowName" type="text" placeholder="Workflow name" style="flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                    <input id="workflowParams" type="text" placeholder='Payload JSON e.g. {"path":"."}' style="flex: 2; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                </div>
                <button class="button" onclick="runWorkflow()" style="margin-top: 10px;">Run workflow</button>
                <pre id="workflowResult">Enter a workflow name and optional parameters, then click Run workflow.</pre>
            </div>
            <div class="card">
                <h2>Memory store</h2>
                <input id="memoryKey" type="text" placeholder="Key" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-bottom: 10px;" />
                <input id="memoryValue" type="text" placeholder="Value" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-bottom: 10px;" />
                <button class="button" onclick="addMemory()">Store memory</button>
                <pre id="memoryStoreResult">Enter a memory key and value, then press Store memory.</pre>
            </div>
            <div class="card">
                <h2>Agents</h2>
                <button class="button" onclick="loadAgents()">Load agents</button>
                <pre id="agents">Press the button to list registered agents.</pre>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                    <input id="agentName" type="text" placeholder="Agent name" style="flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                    <input id="agentPayload" type="text" placeholder='Payload JSON e.g. {"task":"review"}' style="flex: 2; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8;" />
                </div>
                <button class="button" onclick="executeAgent()" style="margin-top: 10px;">Execute agent</button>
                <pre id="agentResult">Enter an agent name and payload, then click Execute agent.</pre>
            </div>
            <div class="card">
                <h2>Approval workflow</h2>
                <input id="approvalAction" type="text" placeholder="Action" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-bottom: 10px;" />
                <input id="approvalDetails" type="text" placeholder="Details" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-bottom: 10px;" />
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
                    <button class="button" onclick="requestApproval()">Request approval</button>
                    <button class="button" onclick="loadApprovals()">List approvals</button>
                </div>
                <pre id="approvalResult">Submit an action and details to generate a new approval request.</pre>
                <input id="approvalId" type="text" placeholder="Approval ID" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #2f436f; background: #0f1730; color: #e6eef8; margin-top: 10px;" />
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px;">
                    <button class="button" onclick="fetchApprovalStatus()">Fetch approval status</button>
                    <button class="button" onclick="decideApproval('approved')">Approve</button>
                    <button class="button" onclick="decideApproval('denied')">Deny</button>
                </div>
                <pre id="approvalStatus">Enter an approval ID and press Fetch approval status.</pre>
            </div>
        </main>
        <script>
            async function loadOverview() {
                const response = await fetch('/api/dashboard/overview');
                const data = await response.json();
                document.getElementById('overview').innerText = JSON.stringify(data, null, 2);
            }
            async function loadVoice() {
                const response = await fetch('/api/voice/status');
                const data = await response.json();
                document.getElementById('voice').innerText = JSON.stringify(data, null, 2);
            }
            async function generateSpeech() {
                const text = document.getElementById('ttsText').value.trim();
                if (!text) {
                    document.getElementById('ttsResult').innerText = 'Please enter text to speak.';
                    return;
                }
                const response = await fetch('/api/voice/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, lang: 'en' })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    const audio = new Audio('data:audio/mpeg;base64,' + data.audio_base64);
                    audio.play();
                    document.getElementById('ttsResult').innerText = 'Speech generated and playing in browser.';
                } else {
                    document.getElementById('ttsResult').innerText = JSON.stringify(data, null, 2);
                }
            }
            async function transcribeAudio() {
                const fileInput = document.getElementById('sttFile');
                if (!fileInput.files.length) {
                    document.getElementById('sttResult').innerText = 'Please choose a WAV file.';
                    return;
                }
                const file = fileInput.files[0];
                const arrayBuffer = await file.arrayBuffer();
                let binary = '';
                const bytes = new Uint8Array(arrayBuffer);
                const chunkSize = 0x8000;
                for (let i = 0; i < bytes.length; i += chunkSize) {
                    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
                }
                const base64 = btoa(binary);
                const response = await fetch('/api/voice/transcribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ audio_base64: base64 })
                });
                const data = await response.json();
                document.getElementById('sttResult').innerText = JSON.stringify(data, null, 2);
            }
            async function searchMemory() {
                const query = document.getElementById('memoryQuery').value;
                if (!query) {
                    document.getElementById('memorySearch').innerText = 'Please enter search text.';
                    return;
                }
                const response = await fetch(`/api/memory/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                document.getElementById('memorySearch').innerText = JSON.stringify(data, null, 2);
            }
            async function loadTools() {
                const response = await fetch('/api/tools/list');
                const data = await response.json();
                document.getElementById('tools').innerText = JSON.stringify(data, null, 2);
            }
            async function executeTool() {
                const toolName = document.getElementById('toolName').value.trim();
                const paramsText = document.getElementById('toolParams').value.trim();
                let params = {};
                if (!toolName) {
                    document.getElementById('toolResult').innerText = 'Please enter a tool name.';
                    return;
                }
                if (paramsText) {
                    try {
                        params = JSON.parse(paramsText);
                    } catch (err) {
                        document.getElementById('toolResult').innerText = 'Invalid JSON parameters.';
                        return;
                    }
                }
                const response = await fetch('/api/tool/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tool_name: toolName, parameters: params })
                });
                const data = await response.json();
                document.getElementById('toolResult').innerText = JSON.stringify(data, null, 2);
            }
            async function executeWebSearch() {
                const query = document.getElementById('webSearchQuery').value.trim();
                if (!query) {
                    document.getElementById('webSearchResult').innerText = 'Please enter a search query.';
                    return;
                }
                const response = await fetch('/api/tool/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tool_name: 'search_web', parameters: { query } })
                });
                const data = await response.json();
                document.getElementById('webSearchResult').innerText = JSON.stringify(data, null, 2);
            }
            async function addMemory() {
                const key = document.getElementById('memoryKey').value.trim();
                const value = document.getElementById('memoryValue').value.trim();
                if (!key || !value) {
                    document.getElementById('memoryStoreResult').innerText = 'Memory key and value are required.';
                    return;
                }
                const response = await fetch('/api/memory/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value })
                });
                const data = await response.json();
                document.getElementById('memoryStoreResult').innerText = JSON.stringify(data, null, 2);
            }
            async function loadAgents() {
                const response = await fetch('/api/agents/list');
                const data = await response.json();
                document.getElementById('agents').innerText = JSON.stringify(data, null, 2);
            }
            async function executeAgent() {
                const agentName = document.getElementById('agentName').value.trim();
                const payloadText = document.getElementById('agentPayload').value.trim();
                let payload = {};
                if (!agentName) {
                    document.getElementById('agentResult').innerText = 'Please enter an agent name.';
                    return;
                }
                if (payloadText) {
                    try {
                        payload = JSON.parse(payloadText);
                    } catch (err) {
                        document.getElementById('agentResult').innerText = 'Invalid JSON payload.';
                        return;
                    }
                }
                const response = await fetch('/api/agent/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_name: agentName, payload })
                });
                const data = await response.json();
                document.getElementById('agentResult').innerText = JSON.stringify(data, null, 2);
            }
            async function requestApproval() {
                const action = document.getElementById('approvalAction').value.trim();
                const details = document.getElementById('approvalDetails').value.trim();
                if (!action || !details) {
                    document.getElementById('approvalResult').innerText = 'Action and details are required.';
                    return;
                }
                const response = await fetch('/api/approval/request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action, details })
                });
                const data = await response.json();
                document.getElementById('approvalResult').innerText = JSON.stringify(data, null, 2);
                if (data.approval_id) {
                    document.getElementById('approvalId').value = data.approval_id;
                }
            }
            async function loadWorkflows() {
                const response = await fetch('/api/automation/list');
                const data = await response.json();
                document.getElementById('workflows').innerText = JSON.stringify(data, null, 2);
            }
            async function runWorkflow() {
                const workflowName = document.getElementById('workflowName').value.trim();
                const paramsText = document.getElementById('workflowParams').value.trim();
                let parameters = {};
                if (!workflowName) {
                    document.getElementById('workflowResult').innerText = 'Please enter a workflow name.';
                    return;
                }
                if (paramsText) {
                    try {
                        parameters = JSON.parse(paramsText);
                    } catch (err) {
                        document.getElementById('workflowResult').innerText = 'Invalid JSON parameters.';
                        return;
                    }
                }
                const response = await fetch('/api/automation/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ workflow_name: workflowName, parameters })
                });
                const data = await response.json();
                document.getElementById('workflowResult').innerText = JSON.stringify(data, null, 2);
            }
            async function loadApprovals() {
                const response = await fetch('/api/approval/list');
                const data = await response.json();
                document.getElementById('approvalResult').innerText = JSON.stringify(data, null, 2);
            }
            async function fetchApprovalStatus() {
                const approvalId = document.getElementById('approvalId').value.trim();
                if (!approvalId) {
                    document.getElementById('approvalStatus').innerText = 'Please enter an approval ID.';
                    return;
                }
                const response = await fetch(`/api/approval/status/${encodeURIComponent(approvalId)}`);
                const data = await response.json();
                document.getElementById('approvalStatus').innerText = JSON.stringify(data, null, 2);
            }
            async function decideApproval(decision) {
                const approvalId = document.getElementById('approvalId').value.trim();
                if (!approvalId) {
                    document.getElementById('approvalStatus').innerText = 'Please enter an approval ID before deciding.';
                    return;
                }
                const response = await fetch('/api/approval/decision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ approval_id: approvalId, decision })
                });
                const data = await response.json();
                document.getElementById('approvalStatus').innerText = JSON.stringify(data, null, 2);
            }
            window.onload = loadOverview;
        </script>
    </body>
    </html>
    """
