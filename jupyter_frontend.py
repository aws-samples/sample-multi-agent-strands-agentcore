#!/usr/bin/env python3
"""
Jupyter-compatible frontend demo using ipywidgets
"""
try:
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    import time
except ImportError:
    print("Installing required packages...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ipywidgets"])
    import ipywidgets as widgets
    from IPython.display import display, HTML, clear_output
    import time
class MultiAgentFrontend:
    def __init__(self):
        self.messages = []
        self.setup_ui()
    def setup_ui(self):
        # Title
        display(HTML("<h1>:robot_face: Multi-Agent Customer Support System</h1>"))
        display(HTML("<p><em>Demo of Lab 5: Multi-Agent Frontend Integration</em></p>"))
        # Status
        display(HTML("""
        <div style='background: #F0F0F0; padding: 10px; border-radius: 5px; margin: 10px 0;'>
        <h3>System Status</h3>
        :white_check_mark: Orchestrator Agent<br>
        :white_check_mark: Customer Support Agent<br>
        :white_check_mark: Knowledge Base Agent<br>
        :bulb: This is a demo interface
        </div>
        """))
        # Chat area
        self.chat_output = widgets.Output()
        display(self.chat_output)
        # Input area
        self.text_input = widgets.Text(
            placeholder="Type your question here...",
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='70%')
        )
        self.send_button = widgets.Button(
            description="Send",
            button_style='primary',
            layout=widgets.Layout(width='15%')
        )
        # Demo buttons
        self.demo1 = widgets.Button(description=":iphone: Product Issue", layout=widgets.Layout(width='30%'))
        self.demo2 = widgets.Button(description=":wrench: Technical Support", layout=widgets.Layout(width='30%'))
        self.demo3 = widgets.Button(description=":clipboard: Account Help", layout=widgets.Layout(width='30%'))
        # Event handlers
        self.send_button.on_click(self.send_message)
        self.text_input.on_submit(self.send_message)
        self.demo1.on_click(lambda b: self.send_demo("My phone screen is cracked, is it covered under warranty?"))
        self.demo2.on_click(lambda b: self.send_demo("How do I reset my device to factory settings?"))
        self.demo3.on_click(lambda b: self.send_demo("I need to update my billing information"))
        # Layout
        input_box = widgets.HBox([self.text_input, self.send_button])
        demo_box = widgets.HBox([self.demo1, self.demo2, self.demo3])
        display(input_box)
        display(HTML("<h3>:dart: Quick Demo Queries</h3>"))
        display(demo_box)
        # Initial message
        self.add_message("assistant", "Hello! I'm your AI customer support assistant. How can I help you today?")
    def send_message(self, b):
        message = self.text_input.value.strip()
        if message:
            self.add_message("user", message)
            self.text_input.value = ""
            self.process_message(message)
    def send_demo(self, message):
        self.add_message("user", message)
        self.process_message(message)
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.update_chat()
    def process_message(self, message):
        # Simulate processing
        with self.chat_output:
            print(":arrows_counterclockwise: Multi-agent system processing...")
        time.sleep(1)  # Simulate processing time
        response = f"""I understand you're asking about: "{message}"
:arrows_counterclockwise: **Multi-Agent Processing:**
1. **Orchestrator**: Routing your query...
2. **Knowledge Base**: Searching relevant information...
3. **Customer Support**: Crafting personalized response...
**Response:** This is a demo interface. In the full system, your query would be processed by multiple specialized agents working together to provide the best possible support.
*To see the actual multi-agent system in action, run the Jupyter notebooks (Lab 1-4) first.*"""
        self.add_message("assistant", response)
    def update_chat(self):
        with self.chat_output:
            clear_output()
            for msg in self.messages:
                role_icon = ":robot_face:" if msg["role"] == "assistant" else ":bust_in_silhouette:"
                print(f"{role_icon} **{msg['role'].title()}:**")
                print(msg["content"])
                print("-" * 50)
def run_frontend():
    """Run the Jupyter-compatible frontend"""
    return MultiAgentFrontend()
if __name__ == "__main__":
    frontend = run_frontend()