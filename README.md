# Browser Agent v12_p

**Minimalistic browser automation with essential functions**

A refined, production-ready browser automation tool built with Playwright. Features clean modular architecture, interactive CLI, and comprehensive element detection capabilities.

## 🚀 Quick Start

```bash
# Clone and setup
cd version_12_p
chmod +x run.sh

# Install dependencies and start
./run.sh

# Or manual setup
pip install -r requirements.txt
playwright install
python main.py
```

## ✨ Features

- **🌐 Smart Navigation** - URL validation and auto-correction
- **🔍 Element Detection** - Find all clickable elements with metadata
- **🖱️ Smart Clicking** - Multiple fallback strategies for reliable interaction
- **📸 Screenshots** - Automatic and manual screenshot capabilities
- **⚙️ Configuration** - Environment-based settings with sensible defaults
- **🎯 Interactive CLI** - Real-time browser control with intuitive commands

## 📁 Architecture

```
version_12_p/
├── main.py          # Entry point & CLI interface
├── config.py        # Configuration management
├── browser.py       # Core browser operations
├── elements.py      # Element detection & interaction
├── controller.py    # Interactive control & UI
├── requirements.txt # Dependencies
└── run.sh          # Setup script
```

## 🎮 Usage

### Interactive Mode (Default)
```bash
python main.py                    # Start interactive mode
python main.py --url google.com   # Navigate and start interactive
```

### Command Examples
```bash
# In interactive mode:
navigate google.com    # Navigate to URL
find                  # Find clickable elements
click 5              # Click element #5
screenshot           # Take screenshot
info                 # Show page info
help                 # Show all commands
```

### Single Command Mode
```bash
python main.py --url google.com --find        # Find elements and exit
python main.py --url google.com --screenshot  # Screenshot and exit
python main.py --url google.com --info        # Page info and exit
```

### Configuration Options
```bash
python main.py --headless false              # Visual browser
python main.py --browser firefox             # Use Firefox
python main.py --verbose                     # Detailed output
python main.py --config custom.env           # Custom config file
```

## ⚙️ Configuration

Create `.env` file for custom settings:

```env
# Browser settings
HEADLESS=true
BROWSER_TYPE=chromium
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720

# Timeout settings (milliseconds)
PAGE_TIMEOUT=30000
ELEMENT_TIMEOUT=5000
NAVIGATION_TIMEOUT=30000

# Screenshot settings
SCREENSHOT_DIR=screenshots
AUTO_SCREENSHOT=true

# Output settings
OUTPUT_DIR=output
VERBOSE=false
```

## 🎯 Commands Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| `navigate <url>` | `n`, `go` | Navigate to URL |
| `elements` | `e`, `find` | Find clickable elements |
| `click <number>` | `c` | Click element by number |
| `screenshot` | `s` | Take screenshot |
| `info` | `i` | Show page information |
| `list` | `l` | List found elements |
| `export` | | Export elements to JSON |
| `help` | `h` | Show help |
| `quit` | `q`, `exit` | Exit application |

### Shortcuts
- Type just a number (e.g., `5`) to click element #5
- Type a URL directly to navigate (e.g., `google.com`)

## 📊 Technical Specs

- **Total Lines**: 730 (core functionality)
- **Files**: 5 core Python modules
- **Dependencies**: Only `playwright` + `python-dotenv`
- **Browser Support**: Chromium, Firefox, WebKit
- **Python**: 3.7+

## 🔧 Development

The codebase follows clean architecture principles:

- **`config.py`** - Environment & settings management
- **`browser.py`** - Browser lifecycle & navigation
- **`elements.py`** - DOM interaction & element analysis
- **`controller.py`** - User interface & command processing
- **`main.py`** - Application orchestration & CLI

## 📈 Performance

- Fast startup (~2-3 seconds)
- Efficient element detection (50 elements max)
- Smart click fallbacks for reliability
- Minimal memory footprint
- Clean resource management

## 🛠️ Troubleshooting

**Browser not starting?**
```bash
playwright install  # Install browser binaries
```

**Permission denied?**
```bash
chmod +x run.sh main.py  # Make scripts executable
```

**Import errors?**
```bash
pip install -r requirements.txt  # Install dependencies
```

## 📝 Examples

### Basic Navigation & Interaction
```bash
$ python main.py
> navigate github.com
> find
Found 15 clickable elements:
  0: Link: Sign in
  1: Link: Sign up
  2: Button: Search
> click 0
✓ Click successful
```

### Automated Screenshot
```bash
$ python main.py --url github.com --screenshot
📸 Taking screenshot...
✓ Screenshot saved: screenshots/screenshot_github_com_20231201_143022.png
```

This is Browser Agent v12_p - refined, minimalistic, and production-ready.