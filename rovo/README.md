# ROVO Browser Agent 🤖

**Minimalistic Agentic Browser Automation Tool**

A fully functional, AI-powered browser automation agent built with CrewAI, Playwright, and Google Gemini. Features autonomous decision-making, multi-agent coordination, and intelligent web interaction capabilities.

## 🚀 Quick Start

```bash
# Clone or navigate to the directory
cd /root/projects/Repositories/browser_agent/rovo

# Setup (one-time)
./run.sh --setup

# Edit configuration
nano .env  # Add your GOOGLE_API_KEY

# Run interactive mode
./run.sh
```

## ✨ Features

- **🤖 Agentic Architecture**: Multi-agent system with specialized roles
- **🧠 AI-Powered**: Google Gemini integration for intelligent decisions
- **🌐 Browser Automation**: Full Playwright integration
- **📊 Monitoring**: Optional AgentOps integration
- **🎮 Interactive CLI**: Real-time command interface
- **⚙️ Configurable**: Environment-based settings

## 🏗️ Architecture

```
ROVO Browser Agent
├── Navigation Agent    # URL management & browser control
├── Element Detective   # Find & analyze page elements
├── Interaction Agent   # Click, fill forms, interactions
└── Web Analyst        # Page analysis & strategy
```

## 📁 Project Structure

```
rovo/
├── main.py              # Entry point & CLI
├── config.py            # Configuration management
├── browser_manager.py   # Browser operations
├── agents.py            # CrewAI agents & workflows
├── agent_tools.py       # Agent tool implementations
├── requirements.txt     # Dependencies
├── setup.sh            # Setup script
├── run.sh              # Runner script
├── .env.sample         # Environment template
└── README.md           # This file
```

## 🎮 Usage

### Interactive Mode (Default)
```bash
./run.sh

# Commands in interactive mode:
ROVO> nav google.com                    # Navigate and analyze
ROVO> goal google.com search for AI     # Goal-based browsing
ROVO> auto google.com search click      # Full automation
ROVO> screenshot                        # Take screenshot
ROVO> info                             # Page information
ROVO> help                             # Show commands
ROVO> quit                             # Exit
```

### Command Line Mode
```bash
# Navigate and analyze
./run.sh --mode nav --url google.com

# Goal-based browsing
./run.sh --mode goal --url google.com --goal "search for python"

# Full automation
./run.sh --mode auto --url google.com --goal "search" --element "search button"

# Run with visible browser
./run.sh --headless false
```

### Python API
```python
from main import RovoBrowserAgent
import asyncio

async def example():
    agent = RovoBrowserAgent()
    await agent.start()
    
    # Simple navigation
    result = agent.navigate_and_analyze("https://google.com")
    print(result)
    
    # Goal-based browsing
    result = agent.goal_based_browsing("https://google.com", "search for AI")
    print(result)
    
    await agent.stop()

asyncio.run(example())
```

## ⚙️ Configuration

Edit `.env` file:

```env
# Browser Settings
HEADLESS=true
BROWSER_TYPE=chromium
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720
PAGE_TIMEOUT=30000

# AI Settings (Required)
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-pro

# AgentOps Settings (Optional)
AGENTOPS_API_KEY=your_agentops_api_key_here
ENABLE_MONITORING=false

# Default Settings
DEFAULT_URL=https://www.google.com
VERBOSE=true
```

### Getting API Keys

1. **Google API Key** (Required):
   - Visit: https://makersuite.google.com/app/apikey
   - Create new API key
   - Add to `.env` file

2. **AgentOps API Key** (Optional):
   - Visit: https://app.agentops.ai
   - Sign up and get API key
   - Add to `.env` file

## 🎯 Use Cases

### 1. Web Research
```bash
ROVO> goal wikipedia.org "research artificial intelligence"
```

### 2. E-commerce Navigation
```bash
ROVO> goal amazon.com "find laptop under $1000"
```

### 3. Form Automation
```bash
ROVO> auto contact-form.com "fill contact form" "submit button"
```

### 4. Content Extraction
```bash
ROVO> nav news-site.com
ROVO> screenshot
```

## 🔧 Development

### Adding New Agents
```python
# In agents.py
def create_custom_agent(self) -> Agent:
    return Agent(
        role='Custom Role',
        goal='Custom goal',
        backstory='Custom backstory',
        tools=[custom_tools],
        verbose=True
    )
```

### Adding New Tools
```python
# In agent_tools.py
class CustomTool(BaseTool):
    name: str = "custom_tool"
    description: str = "Custom tool description"
    
    def _run(self, input_str: str) -> str:
        # Tool implementation
        return "Tool result"
```

### Custom Workflows
```python
# In agents.py
def execute_custom_workflow(self, params) -> str:
    tasks = [
        self.create_custom_task(params),
        # More tasks...
    ]
    
    crew = Crew(
        agents=[self.custom_agent],
        tasks=tasks,
        process=Process.sequential
    )
    
    return crew.kickoff()
```

## 📊 Technical Specs

- **Total Lines**: ~800 lines of core functionality
- **Files**: 6 core Python modules
- **Dependencies**: CrewAI, Playwright, Google Generative AI
- **Browser Support**: Chromium, Firefox, WebKit
- **Python**: 3.8+

## 🛠️ Troubleshooting

### Setup Issues
```bash
# If setup fails
python3 --version  # Check Python 3.8+
pip install --upgrade pip
./setup.sh
```

### Browser Issues
```bash
# If browser doesn't start
playwright install chromium
# Or try different browser
export BROWSER_TYPE=firefox
```

### API Issues
```bash
# Check API key
grep GOOGLE_API_KEY .env
# Test API connection
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('API OK')"
```

### Permission Issues
```bash
chmod +x setup.sh run.sh main.py
```

## 📈 Performance

- **Startup Time**: ~3-5 seconds
- **Navigation**: ~2-3 seconds per page
- **Element Detection**: ~1-2 seconds
- **AI Analysis**: ~2-5 seconds (depends on complexity)
- **Memory Usage**: ~100-200MB

## 🔒 Security

- Environment variables for sensitive data
- No hardcoded credentials
- Secure browser configuration
- Input validation and sanitization

## 📝 Examples

### Example 1: Research Workflow
```bash
./run.sh --mode goal --url "https://en.wikipedia.org" --goal "research machine learning"
```

### Example 2: Shopping Assistant
```bash
./run.sh --mode auto --url "https://amazon.com" --goal "find books" --element "search"
```

### Example 3: News Analysis
```bash
./run.sh --mode nav --url "https://news.ycombinator.com"
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check README.md
- **API Keys**: Follow setup instructions
- **Browser Issues**: Run `playwright install`

---

**ROVO Browser Agent** - Autonomous web browsing made simple! 🚀