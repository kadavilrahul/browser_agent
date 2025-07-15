# Web Browsing Agent

A comprehensive web automation tool that can navigate websites and perform complex interactions using Playwright.

## Quick Start (No README Required!)

**Just run the script and follow the interactive prompts:**

```bash
# Make executable and run
chmod +x run.sh
./run.sh
```

The script will automatically:
- Check your system requirements
- Install all dependencies
- Set up the environment
- Guide you through all options with numbered menus
- Handle everything end-to-end

**That's it! No need to read further unless you want technical details.**

---

## Features

- Web automation using Playwright
- Headless and non-headless mode support
- Predefined and custom task execution
- Real-time web element analysis
- Interactive browser control
- Automated login capabilities
- Web scraping and element identification

## Technical Details (Optional Reading)

### System Requirements

- Python 3.8 or higher
- 2GB+ RAM
- Internet connection for downloading browser binaries

### Manual Installation (if needed)

The run.sh script handles everything automatically, but if you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment file
cp sample.env .env

# Run the application
python unified_web_agent.py
```

### Application Modes

1. **Interactive Mode**: Real-time browser control with commands
2. **Login Mode**: Automated website login assistant  
3. **Scraper Mode**: Analyze and extract clickable elements from webpages
4. **Navigate Mode**: Simple webpage navigation with screenshot

### Configuration

The application uses environment variables for configuration. Key settings:

- `HEADLESS`: Run browser in headless mode (true/false)
- `BROWSER_TIMEOUT`: Timeout for browser operations (milliseconds)
- `VIEWPORT_WIDTH/HEIGHT`: Browser window dimensions
- `LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARNING/ERROR)

### Troubleshooting

If you encounter issues:

1. **Run the interactive setup**: `./run.sh` and choose setup option
2. **Check system status**: `./run.sh status`
3. **View logs**: Check `web_agent.log` for detailed error messages
4. **Re-run setup**: `./run.sh setup`

### Command Line Usage

```bash
./run.sh                          # Interactive menu (recommended)
./run.sh setup                    # Run setup only
./run.sh interactive              # Interactive browser mode
./run.sh login                    # Login mode
./run.sh scraper <url>            # Web scraper mode
./run.sh navigate <url>           # Navigation mode
./run.sh status                   # Check system status
```

### File Structure

```
.
├── run.sh                 # Main launcher script
├── unified_web_agent.py   # Core application
├── test_setup.py         # Setup verification
├── requirements.txt      # Python dependencies
├── sample.env           # Environment template
├── .env                 # Your configuration
└── web_agent.log        # Application logs
```

## License

This project is provided as-is for educational and automation purposes.