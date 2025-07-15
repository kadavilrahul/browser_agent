#!/bin/bash
# Script to find and save all clickable elements from a webpage

# Default URL and output file
URL=${1:-"https://github.com"}
OUTPUT_FILE=${2:-"clickable_elements.json"}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if Playwright is installed globally
if ! npx playwright --version &> /dev/null; then
    echo "Error: Playwright is not installed globally. Please run playwright_install.sh first."
    exit 1
fi

echo "Finding clickable elements from $URL..."

# Create permanent JS file in project directory
JS_SCRIPT="find_clickables.js"
cat > "$JS_SCRIPT" <<'JS_SCRIPT'
const { chromium } = require('playwright');
const [url, outputFile] = process.argv.slice(2);

(async () => {
  try {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    
    await page.goto(url);
    
    const clickables = await page.$$eval('a, button, [role=button], input[type=button], input[type=submit]',
      elements => elements.map((el, i) => ({
        index: `[${i}]`,
        tag: el.tagName,
        text: el.innerText.trim(),
        href: el.href || null,
        id: el.id || null,
        class: el.className || null
      })));

    require('fs').writeFileSync(outputFile, JSON.stringify(clickables, null, 2));
    console.log(`Saved clickable elements to ${outputFile}`);
    console.log('Browser window will remain open for inspection');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
})();
JS_SCRIPT

# Execute the script
node "$JS_SCRIPT" "$URL" "$OUTPUT_FILE"
SCRIPT_EXIT_CODE=$?

# Clean up
rm "$JS_SCRIPT"

if [ $SCRIPT_EXIT_CODE -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "Successfully saved clickable elements to $OUTPUT_FILE"
else
    echo "Failed to save clickable elements"
    exit 1
fi