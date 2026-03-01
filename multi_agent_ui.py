#!/usr/bin/env python3
"""
Multi-Agent UI for Lab-4 Runtime Integration
Connects to deployed orchestrator, customer support, and knowledge base agents via HTTP
"""

try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    import time
    import json
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ipywidgets"])
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    import time
    import json

import requests
import urllib.parse
from uuid import uuid4
import boto3
from lab_helpers.utils import get_ssm_parameter, setup_or_reuse_cognito_user_pool

# Get region
session = boto3.Session()
REGION = session.region_name or "us-west-2"

# A2A agents require JSON-RPC 2.0 format
A2A_AGENTS = ["customer_support", "knowledge_base"]

class MultiAgentUI:
    def __init__(self):
        self.messages = []
        self.current_agent = "orchestrator"
        # Cache for agent ARNs and bearer token (lazy initialization)
        self._agent_arns = {}
        self._bearer_token = None
        self._cognito_config = None
        self.setup_ui()
    
    def _get_agent_arn(self, agent_type):
        """Get agent ARN from cache or SSM (lazy initialization)"""
        if agent_type not in self._agent_arns:
            try:
                self._agent_arns[agent_type] = get_ssm_parameter(f"/app/reinvent/agentcore/{agent_type}_arn")
            except Exception as e:
                raise Exception(f"Failed to get {agent_type} ARN from SSM: {e}")
        return self._agent_arns[agent_type]
    
    def _get_bearer_token(self):
        """Get bearer token from Cognito (lazy initialization)"""
        if self._bearer_token is None:
            try:
                # Get fresh Cognito config with bearer token
                # This reuses existing pool and gets a fresh token
                if self._cognito_config is None:
                    self._cognito_config = setup_or_reuse_cognito_user_pool()
                
                self._bearer_token = self._cognito_config.get('Bearer Token')
                if not self._bearer_token:
                    raise Exception("Bearer token not found in Cognito config")
                    
            except Exception as e:
                raise Exception(f"Failed to get bearer token from Cognito: {e}")
        return self._bearer_token
    
    def setup_ui(self):
        # Title
        display(HTML("<h1>🤖 Multi-Agent Customer Support System</h1>"))
        display(HTML("<p><em>Lab-4 Runtime Integration - Live Agent System</em></p>"))
        
        # Agent status
        display(HTML("""
        <div style='background: #E8F5E8; padding: 15px; border-radius: 8px; margin: 10px 0;'>
        <h3>🟢 Active Agent Runtimes</h3>
        ✅ <strong>Orchestrator Agent</strong> - Routes queries intelligently<br>
        ✅ <strong>Customer Support Agent</strong> - Product info, returns, policies<br>
        ✅ <strong>Knowledge Base Agent</strong> - Technical troubleshooting<br>
        </div>
        """))
        
        # Agent selector
        self.agent_selector = widgets.Dropdown(
            options=[
                ('🎯 Orchestrator (Smart Routing)', 'orchestrator'),
                ('🛍️ Customer Support', 'customer_support'), 
                ('🔧 Technical Support', 'knowledge_base')
            ],
            value='orchestrator',
            description='Agent:',
            style={'description_width': 'initial'}
        )
        self.agent_selector.observe(self.on_agent_change, names='value')
        
        # Chat area
        self.chat_output = widgets.Output()
        display(self.chat_output)
        
        # Input controls
        self.text_input = widgets.Text(
            placeholder="Ask your question...",
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='70%')
        )
        self.send_button = widgets.Button(
            description="Send",
            button_style='primary',
            layout=widgets.Layout(width='15%')
        )
        
        # Event handlers
        self.send_button.on_click(self.send_message)
        self.text_input.on_submit(self.send_message)
        
        # Layout
        display(self.agent_selector)
        input_box = widgets.HBox([self.text_input, self.send_button])
        display(input_box)
        
        # Welcome message
        self.add_message("assistant", "Hello! I'm your multi-agent customer support system. Choose an agent above or let the Orchestrator route your query automatically. How can I help you today?")
    
    def on_agent_change(self, change):
        self.current_agent = change['new']
        agent_names = {
            'orchestrator': 'Orchestrator Agent',
            'customer_support': 'Customer Support Agent', 
            'knowledge_base': 'Knowledge Base Agent'
        }
        self.add_message("system", f"Switched to {agent_names[self.current_agent]}")
    
    def send_message(self, b):
        message = self.text_input.value.strip()
        if message:
            self.add_message("user", message)
            self.text_input.value = ""
            self.process_message(message)
    

    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.update_chat()
    
    def process_message(self, message):
        with self.chat_output:
            print(f"🔄 Processing with {self.current_agent} agent...")
        
        try:
            # Get agent ARN and bearer token using lazy initialization
            agent_arn = self._get_agent_arn(self.current_agent)
            bearer_token = self._get_bearer_token()
            
            # Build invocation URL
            encoded_arn = urllib.parse.quote(agent_arn, safe='')
            url = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{encoded_arn}/invocations/"
            
            # Prepare payload based on agent type
            if self.current_agent in A2A_AGENTS:
                # A2A agents use JSON-RPC 2.0 format
                message_id = str(uuid4())
                session_id = str(uuid4())
                
                payload = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"kind": "text", "text": message}],
                            "messageId": message_id
                        }
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {bearer_token}",
                    "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
                    "Content-Type": "application/json"
                }
            else:
                # Orchestrator uses simple prompt format
                payload = {"prompt": message}
                headers = {
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json"
                }
            
            # Make HTTP request
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            # Extract response text
            if self.current_agent in A2A_AGENTS and "result" in result:
                # Extract from A2A response format
                response_text = ""
                if "artifacts" in result["result"]:
                    for artifact in result["result"]["artifacts"]:
                        if "parts" in artifact:
                            for part in artifact["parts"]:
                                if part.get("kind") == "text":
                                    response_text = part.get("text", "")
                                    break
                if not response_text:
                    response_text = str(result)
            else:
                # Orchestrator response
                response_text = str(result)
            
            agent_names = {
                'orchestrator': '🎯 Orchestrator Agent',
                'customer_support': '🛍️ Customer Support Agent',
                'knowledge_base': '🔧 Knowledge Base Agent'
            }
            
            formatted_response = f"**{agent_names[self.current_agent]} Response:**\n\n{response_text}"
            self.add_message("assistant", formatted_response)
            
        except Exception as e:
            error_msg = f"❌ Error processing request: {str(e)}\n\nPlease ensure all lab-4 agents are deployed and the Cognito token is valid."
            self.add_message("assistant", error_msg)
    
    def update_chat(self):
        with self.chat_output:
            clear_output()
            for msg in self.messages[-10:]:  # Show last 10 messages
                if msg["role"] == "system":
                    print(f"ℹ️ {msg['content']}")
                elif msg["role"] == "user":
                    print(f"👤 **You:** {msg['content']}")
                elif msg["role"] == "assistant":
                    print(f"🤖 {msg['content']}")
                print("-" * 60)

def run_multi_agent_ui():
    """Launch the multi-agent UI"""
    return MultiAgentUI()

if __name__ == "__main__":
    ui = MultiAgentUI()