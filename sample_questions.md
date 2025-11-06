# Sample Questions for Multi-Agent Customer Support System

## 🤖 Lab 1: Multi-Agent Foundation Questions
*Tests basic orchestrator coordination with specialized agents*

### Product Information (Customer Support Agent)
- "What are the technical specifications for your laptops?"
- "Do you have wireless headphones with noise cancellation?"
- "What's the warranty coverage on smartphones?"
- "Can you tell me about your monitor selection?"

### Return Policy (Customer Support Agent)
- "What's your return policy for electronics?"
- "How long do I have to return a laptop?"
- "Can I return opened headphones?"
- "What condition do items need to be in for returns?"

### General Web Search (Customer Support Agent)
- "What are the latest smartphone trends in 2024?"
- "How do I troubleshoot Bluetooth connectivity issues?"
- "What's the difference between OLED and LCD displays?"

### Technical Documentation (Knowledge Base Agent)
- "How do I set up dual monitors?"
- "My laptop won't turn on, what should I check?"
- "How do I optimize battery life on my device?"
- "What are the system requirements for video editing?"

---

## 🧠 Lab 2: Memory Integration Questions
*Tests persistent memory across conversation sessions*

### Conversation Continuity
- **First message**: "I'm looking for a new laptop for video editing"
- **Follow-up**: "What about the one we discussed earlier?" *(should remember laptop context)*
- **Later**: "Can you remind me what we talked about?" *(should recall conversation history)*

### Customer Context Building
- "I bought a laptop from you last month"
- "I'm having issues with the device we discussed"
- "What was that return policy you mentioned?"
- "Can you look up my previous questions about monitors?"

### Multi-Turn Technical Support
- **Turn 1**: "My laptop is running slowly"
- **Turn 2**: "I tried that, what else can I do?" *(should remember previous suggestions)*
- **Turn 3**: "The performance is still poor after those steps" *(should build on conversation)*

---

## 🔧 Lab 3: Gateway Integration Questions
*Tests secure tool sharing via AgentCore Gateway*

### Cross-Agent Tool Usage
- "I need help with a laptop that won't start, and I want to know your return policy"
- "Can you search for troubleshooting guides and check warranty information?"
- "What's the latest on laptop technology, and do you have technical specs?"

### Complex Multi-Tool Scenarios
- "I'm comparing monitors - need specs, reviews, and setup instructions"
- "Help me troubleshoot my headphones and find replacement options"
- "I want to return a smartphone - need policy info and technical alternatives"

---

## 🚀 Lab 4: Production Runtime Questions
*Tests production deployment with observability*

### High-Load Scenarios
- "I need immediate help with multiple devices not working"
- "Can you handle several questions at once about different products?"
- "I'm a business customer with urgent technical support needs"

### Error Recovery Testing
- "What happens if one of your systems is down?"
- "Can you still help if some services are unavailable?"
- "I need backup options for critical support issues"

### Performance Monitoring
- "How quickly can you process complex technical questions?"
- "Can you handle multiple customers asking similar questions?"
- "What's your response time for urgent support requests?"

---

## 🌐 Lab 5: Frontend Integration Questions
*Tests customer-facing interface*

### Natural Conversation Flow
- "Hi, I need help with my electronics"
- "I'm not very technical, can you explain things simply?"
- "Can you walk me through this step by step?"

### Demo Scenarios (Built into Frontend)
- **📦 Order Tracking**: "I need to track my order #12345"
- **🔧 Technical Support**: "My device isn't working properly"
- **💰 Billing Questions**: "I have a question about my bill"

### User Experience Testing
- "Can you help me find the right product for my needs?"
- "I'm confused about your return process"
- "What's the best way to contact technical support?"

---

## 🎯 Advanced Multi-Agent Scenarios

### Complex Orchestration
- "I bought a laptop that's not working, need troubleshooting, warranty info, and return options if needed"
- "Compare your top 3 smartphones with technical specs, reviews, and setup guides"
- "I'm setting up a home office - need monitor recommendations, setup help, and compatibility info"

### Edge Cases
- "I have a very unusual technical problem that might need multiple experts"
- "Can you help with a product that's not in your standard catalog?"
- "I need support for a complex multi-device setup"

### Business Customer Scenarios
- "I'm purchasing equipment for 50 employees, need bulk pricing and technical support"
- "We need enterprise-level support for our technology deployment"
- "Can you provide technical documentation for our IT team?"

---

## 🧪 Testing Different Agent Capabilities

### Orchestrator Intelligence
- "I'm not sure which department can help me with this issue"
- "Can you figure out what kind of support I need?"
- "I have multiple problems - can you prioritize them?"

### Customer Support Agent
- "What products do you recommend for gaming?"
- "I need help understanding your warranty terms"
- "Can you search for the latest product reviews?"

### Knowledge Base Agent
- "I need detailed technical documentation"
- "Can you provide step-by-step troubleshooting?"
- "What are the advanced configuration options?"

### Memory System
- "Remember that I prefer budget-friendly options"
- "Keep track of my technical skill level for future conversations"
- "Can you recall what we discussed in our last session?"

---

## 💡 Tips for Testing

1. **Start Simple**: Begin with basic single-agent questions
2. **Build Complexity**: Progress to multi-agent coordination scenarios
3. **Test Memory**: Use follow-up questions that reference previous context
4. **Check Error Handling**: Try questions outside the system's knowledge
5. **Validate Orchestration**: Ask questions that require multiple agents
6. **Test Production Features**: Try high-load and edge case scenarios

Each question type tests different aspects of your multi-agent system, from basic tool usage to complex cross-agent coordination with memory persistence and production reliability.