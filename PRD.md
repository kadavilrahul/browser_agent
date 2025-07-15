# Product Requirements Document (PRD) - Browser Agent Version 12_p

## Project Overview
**Version**: 12_p (Minimalistic & Production-ready)
**Goal**: Create a refined, minimalistic browser automation agent with essential functions only
**Architecture**: Clean modular design with minimal dependencies

## Core Requirements

### 1. Essential Functions Only
- Browser initialization and management
- URL navigation with smart handling
- Element detection and interaction
- Screenshot capabilities
- Basic configuration management
- Simple interactive control

### 2. Minimalistic Design Principles
- **Maximum 5 files** (excluding README and requirements.txt)
- **Under 800 total lines of code**
- **Minimal dependencies** (playwright + python-dotenv only)
- **Single responsibility per module**
- **No AI/LLM integration** (keep it simple)

## Planned File Structure

```
version_12_p/
├── README.md                 (~50 lines)
├── requirements.txt          (~3 lines)
├── run.sh                   (~10 lines)
├── config.py                (~80 lines)  # Configuration management
├── browser.py               (~200 lines) # Core browser operations
├── elements.py              (~150 lines) # Element detection & interaction
├── controller.py            (~180 lines) # Interactive control & CLI
└── main.py                  (~120 lines) # Entry point & orchestration
```

## Detailed File Specifications

### 1. main.py (~120 lines)
**Purpose**: Application entry point and orchestration
**Key Functions**:
- Command-line argument parsing
- Application initialization
- Mode selection (interactive, navigate, screenshot)
- Error handling and cleanup
- Exit management

### 2. config.py (~80 lines)
**Purpose**: Configuration management and environment handling
**Key Functions**:
- Environment variable loading
- Default configuration values
- Browser options management
- Timeout and viewport settings
- Boolean configuration parsing

### 3. browser.py (~200 lines)
**Purpose**: Core browser operations and lifecycle management
**Key Functions**:
- Browser initialization with proper configuration
- Context and page management
- Navigation with smart waiting
- Screenshot functionality
- Cleanup and resource management
- Error handling for browser operations

### 4. elements.py (~150 lines)
**Purpose**: Element detection, analysis, and interaction
**Key Functions**:
- Comprehensive clickable element detection
- Element metadata extraction
- Click operations with fallback strategies
- Element indexing and JSON export
- Interactive element selection

### 5. controller.py (~180 lines)
**Purpose**: Interactive control and user interface
**Key Functions**:
- Command-line interface
- User input handling
- Interactive menu system
- Element selection interface
- Command execution
- Session state display

## Dependencies
```
playwright==1.41.1
python-dotenv==1.0.0
```

## Key Features

### Core Browser Operations
- ✅ Initialize browser (headless/non-headless)
- ✅ Navigate to URLs with validation
- ✅ Handle page loading states
- ✅ Automatic screenshot generation
- ✅ Proper cleanup and context management

### Element Interaction
- ✅ Detect all clickable elements
- ✅ Extract element metadata (text, tag, attributes)
- ✅ Click elements with smart fallback
- ✅ Export elements to JSON format
- ✅ Interactive element selection

### User Interface
- ✅ Simple command-line interface
- ✅ Interactive mode for real-time control
- ✅ Clear status messages and error handling
- ✅ Easy navigation and element interaction

### Configuration
- ✅ Environment-based configuration
- ✅ Headless mode toggle
- ✅ Timeout and viewport settings
- ✅ Screenshot quality options

## Success Criteria

### Code Quality
- [ ] Under 800 total lines of code
- [ ] Maximum 5 core files (plus README, requirements, run script)
- [ ] Clean, readable, and well-structured code
- [ ] Proper error handling throughout
- [ ] No external AI/LLM dependencies

### Functionality
- [ ] Can navigate to any URL successfully
- [ ] Can detect and interact with page elements
- [ ] Can take screenshots automatically
- [ ] Interactive mode works smoothly
- [ ] Proper configuration management

### Usability
- [ ] Easy installation with single script
- [ ] Clear and intuitive command-line interface
- [ ] Helpful error messages and user guidance
- [ ] Fast startup and responsive interaction

## Implementation Timeline
1. **Setup & Configuration** (config.py, requirements.txt, run.sh)
2. **Core Browser Operations** (browser.py)
3. **Element Detection** (elements.py)
4. **Interactive Control** (controller.py)
5. **Main Orchestration** (main.py)
6. **Testing & Refinement**

## Line Count Estimate Summary
| File | Estimated Lines | Purpose |
|------|----------------|---------|
| main.py | 120 | Entry point & orchestration |
| config.py | 80 | Configuration management |
| browser.py | 200 | Core browser operations |
| elements.py | 150 | Element detection & interaction |
| controller.py | 180 | Interactive control & CLI |
| **Total Core Code** | **730** | **All functionality** |
| README.md | 50 | Documentation |
| requirements.txt | 3 | Dependencies |
| run.sh | 10 | Setup script |
| **Grand Total** | **793** | **Complete package** |

This design ensures a clean, minimalistic, yet fully functional browser automation agent that incorporates the best practices learned from all previous versions while maintaining simplicity and ease of use.