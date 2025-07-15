# Browser Automation Tools

This project provides scripts for browser automation using Playwright.

## Scripts

### playwright_install.sh
Installs Playwright and required browsers globally:
```bash
bash playwright_install.sh
```

### open_browser.sh
Opens a browser to a specified URL (default: example.com):
```bash
bash open_browser.sh [URL]
```

### find_clickables.sh
Finds and saves all clickable elements from a webpage:
```bash
bash find_clickables.sh [URL] [OUTPUT_FILE]
```
- URL: Webpage to analyze (default: https://example.com)
- OUTPUT_FILE: JSON file to save results (default: clickable_elements.json)

The browser will remain open after execution for inspection.

## Requirements
- Node.js (v18+ recommended)
- npm

## Installation Options

### Global Installation (recommended)
```bash
bash playwright_install.sh
```

### Local Installation (project-specific)
```bash
bash local_install.sh
```

### After Installation
You can then use the other scripts:
```bash
bash open_browser.sh
bash find_clickables.sh
```