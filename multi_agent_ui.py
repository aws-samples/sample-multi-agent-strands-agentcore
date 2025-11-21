#!/usr/bin/env python3
"""
Multi-Agent UI for Lab-4 Runtime Integration
Connects to orchestrator, customer support, and knowledge base agents
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

# Import the agent runtimes
from lab_helpers.runtime.orchestrator_runtime import orchestrator
from lab_helpers.runtime.customer_support_runtime import customer_support_agent
from lab_helpers.runtime.knowledge_base_runtime import knowledge_base_agent

class MultiAgentUI:
    def __init__(self):
        self.messages = []
        self.current_agent = "orchestrator"
        self.setup_ui()
    
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
            # Route to appropriate agent
            if self.current_agent == "orchestrator":
                response = orchestrator(message)
                agent_info = "🎯 Orchestrator Agent"
            elif self.current_agent == "customer_support":
                response = customer_support_agent(message)
                agent_info = "🛍️ Customer Support Agent"
            elif self.current_agent == "knowledge_base":
                response = knowledge_base_agent(message)
                agent_info = "🔧 Knowledge Base Agent"
            
            # Extract response text
            if hasattr(response, 'message'):
                response_text = response.message["content"][0]["text"]
            else:
                response_text = str(response)
            
            formatted_response = f"**{agent_info} Response:**\n\n{response_text}"
            self.add_message("assistant", formatted_response)
            
        except Exception as e:
            error_msg = f"❌ Error processing request: {str(e)}\n\nPlease ensure all lab-4 prerequisites are set up correctly."
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