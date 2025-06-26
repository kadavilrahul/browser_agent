#!/bin/bash

# Comprehensive Shell Script Runner
# Includes all functions from shell scripts in the repository
# Author: Auto-generated from repository scripts
# Date: $(date)

set -e  # Exit on any error

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$(pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"
BACKUPS_DIR="$SCRIPT_DIR/backups"
PID_FILE="$SCRIPT_DIR/.file_versioning.pid"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print section header
print_header() {
    local title=$1
    echo
    print_color "$CYAN" "============================================"
    print_color "$WHITE" "$title"
    print_color "$CYAN" "============================================"
    echo
}

# Print success message
print_success() {
    print_color "$GREEN" "✅ $1"
}

# Print error message
print_error() {
    print_color "$RED" "❌ $1"
}

# Print warning message
print_warning() {
    print_color "$YELLOW" "⚠️  $1"
}

# Print info message
print_info() {
    print_color "$BLUE" "ℹ️  $1"
}

# Check if command exists
cmd_exists() {
    command -v "$1" &>/dev/null
}

# Cleanup function for temporary files
cleanup() {
    rm -f "$REPORTS_DIR/project_structure.txt" "$REPORTS_DIR/sensitive_info.txt" "$REPORTS_DIR/line_counts.txt"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# ============================================================================
# PROJECT INFORMATION FUNCTIONS (from scripts_01/00_generate_project_info.sh)
# ============================================================================

# Function to generate tree structure
generate_tree() {
    local dir="$1"
    local prefix="$2"
    local is_last="$3"
    
    # Skip if directory doesn't exist or is excluded
    if [ ! -d "$dir" ]; then
        return
    fi
    
    # Get list of items, excluding unnecessary files and directories
    local items=()
    while IFS= read -r -d '' item; do
        local basename=$(basename "$item")
        # Skip hidden files and unnecessary files/directories
        if [[ ! "$basename" =~ ^\. ]] && \
           [[ "$basename" != "node_modules" ]] && \
           [[ "$basename" != "__pycache__" ]] && \
           [[ "$basename" != "venv" ]] && \
           [[ "$basename" != "env" ]] && \
           [[ "$basename" != ".venv" ]] && \
           [[ "$basename" != "dist" ]] && \
           [[ "$basename" != "build" ]] && \
           [[ "$basename" != "target" ]] && \
           [[ "$basename" != "bin" ]] && \
           [[ "$basename" != "obj" ]] && \
           [[ "$basename" != ".next" ]] && \
           [[ "$basename" != ".nuxt" ]] && \
           [[ "$basename" != "coverage" ]] && \
           [[ "$basename" != ".pytest_cache" ]] && \
           [[ "$basename" != ".mypy_cache" ]] && \
           [[ "$basename" != "*.log" ]] && \
           [[ "$basename" != "*.tmp" ]] && \
           [[ "$basename" != "*.cache" ]] && \
           [[ ! "$basename" =~ \.env$ ]] && \
           [[ ! "$basename" =~ \.env\. ]] && \
           [[ ! "$basename" =~ \.pyc$ ]] && \
           [[ ! "$basename" =~ \.pyo$ ]] && \
           [[ ! "$basename" =~ \.class$ ]] && \
           [[ ! "$basename" =~ \.o$ ]] && \
           [[ ! "$basename" =~ \.so$ ]] && \
           [[ ! "$basename" =~ \.dll$ ]] && \
           [[ ! "$basename" =~ \.exe$ ]] && \
           [[ ! "$basename" =~ \.DS_Store$ ]] && \
           [[ ! "$basename" =~ Thumbs\.db$ ]]; then
            items+=("$item")
        fi
    done < <(find "$dir" -maxdepth 1 -mindepth 1 -print0 | sort -z)
    
    local count=${#items[@]}
    local i=0
    
    for item in "${items[@]}"; do
        i=$((i + 1))
        local is_last_item=false
        if [ $i -eq $count ]; then
            is_last_item=true
        fi
        
        local basename=$(basename "$item")
        
        if [ -d "$item" ]; then
            if $is_last_item; then
                echo "${prefix}└── $basename/"
                generate_tree "$item" "${prefix}    " true
            else
                echo "${prefix}├── $basename/"
                generate_tree "$item" "${prefix}│   " false
            fi
        else
            if $is_last_item; then
                echo "${prefix}└── $basename"
            else
                echo "${prefix}├── $basename"
            fi
        fi
    done
}

# Generate project information
generate_project_info() {
    local directory="${1:-.}"
    
    print_header "Generating Project Information"
    
    print_info "Gathering project information for: $directory"
    
    # Generate project structure
    print_info "Generating project structure..."
    {
        echo "=== Project Structure ==="
        if cmd_exists tree; then
            # Use tree if available with comprehensive exclusions
            tree "$directory" -a -I '.git|.svn|.hg|node_modules|__pycache__|venv|env|.venv|dist|build|target|bin|obj|.next|.nuxt|coverage|.pytest_cache|.mypy_cache|*.pyc|*.pyo|*.class|*.o|*.so|*.dll|*.exe|*.log|*.tmp|*.cache|.env|.env.*|.DS_Store|Thumbs.db'
        else
            # Fallback to custom tree function
            echo "$(basename "$directory")/"
            generate_tree "$directory" "" true
        fi
    } > "$REPORTS_DIR/project_structure.txt"
    
    # Search for sensitive information
    print_info "Scanning for sensitive information..."
    {
        echo "=== Sensitive Information Scan ==="
        if grep -i -r --exclude="sensitive_info.txt" --exclude="project_info.txt" \
             --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="__pycache__" \
             --exclude-dir="venv" --exclude-dir="env" --exclude-dir=".venv" \
             --exclude-dir="dist" --exclude-dir="build" --exclude-dir="target" \
             --exclude-dir="bin" --exclude-dir="obj" --exclude-dir=".next" \
             --exclude-dir=".nuxt" --exclude-dir="coverage" --exclude-dir=".pytest_cache" \
             --exclude-dir=".mypy_cache" --exclude="*.pyc" --exclude="*.pyo" \
             --exclude="*.class" --exclude="*.log" --exclude="*.tmp" \
             -E "(API_KEY|SECRET|PASSWORD|TOKEN|DATABASE_URL)" "$directory" 2>/dev/null; then
            echo ""
            echo "⚠️  WARNING: Potential sensitive information found above!"
        else
            echo "✅ No sensitive patterns found"
        fi
    } > "$REPORTS_DIR/sensitive_info.txt"
    
    # Count lines of code for various file types
    print_info "Counting lines of code..."
    {
        echo "=== Line Counts ==="
        
        # Find and count lines for each file type, excluding unnecessary directories and files
        total_lines=0
        file_count=0
        
        for file in $(find "$directory" -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" \
                             -o -name "*.java" -o -name "*.c" -o -name "*.cpp" -o -name "*.sh" -o -name "*.go" \
                             -o -name "*.rb" -o -name "*.php" -o -name "*.html" -o -name "*.css" -o -name "*.scss" \
                             -o -name "*.json" -o -name "*.xml" -o -name "*.yaml" -o -name "*.yml" \) \
                             -not -path '*/node_modules/*' \
                             -not -path '*/__pycache__/*' \
                             -not -path '*/venv/*' \
                             -not -path '*/env/*' \
                             -not -path '*/.venv/*' \
                             -not -path '*/dist/*' \
                             -not -path '*/build/*' \
                             -not -path '*/target/*' \
                             -not -path '*/bin/*' \
                             -not -path '*/obj/*' \
                             -not -path '*/.next/*' \
                             -not -path '*/.nuxt/*' \
                             -not -path '*/coverage/*' \
                             -not -path '*/.pytest_cache/*' \
                             -not -path '*/.mypy_cache/*' \
                             -not -path '*/.git/*' \
                             2>/dev/null); do
            if [ -f "$file" ]; then
                lines=$(wc -l < "$file" 2>/dev/null || echo 0)
                echo "$lines $file"
                total_lines=$((total_lines + lines))
                file_count=$((file_count + 1))
            fi
        done
        
        echo ""
        echo "📊 Summary:"
        echo "Total files: $file_count"
        echo "Total lines: $total_lines"
        
        if [ $file_count -eq 0 ]; then
            echo "No code files found"
        fi
    } > "$REPORTS_DIR/line_counts.txt"
    
    # Store project information
    print_info "Creating project_info.txt..."
    {
        echo "=== PROJECT INFORMATION ==="
        echo "Generated on: $(date)"
        echo ""
        cat "$REPORTS_DIR/project_structure.txt"
        echo ""
        cat "$REPORTS_DIR/sensitive_info.txt"
        echo ""
        cat "$REPORTS_DIR/line_counts.txt"
    } > "$REPORTS_DIR/project_info.txt"
    
    print_success "Project information saved to $REPORTS_DIR/project_info.txt"
    print_info "Individual reports: $REPORTS_DIR/project_structure.txt, $REPORTS_DIR/sensitive_info.txt, $REPORTS_DIR/line_counts.txt"
}

# ============================================================================
# CLOC FUNCTIONS (from scripts_01/cloc.sh and scripts_02/run_cloc.sh)
# ============================================================================

# Install and run cloc
install_and_run_cloc() {
    local path="${1:-.}"
    
    print_header "Code Line Counter (CLOC)"
    
    # Install cloc if it's not already installed
    if ! cmd_exists cloc; then
        print_info "Installing cloc..."
        if cmd_exists apt-get; then
            sudo apt-get update
            sudo apt-get install cloc -y
        elif cmd_exists yum; then
            sudo yum install cloc -y
        elif cmd_exists brew; then
            brew install cloc
        else
            print_error "Cannot install cloc automatically. Please install it manually."
            return 1
        fi
    else
        print_success "cloc is already installed."
    fi
    
    # Run cloc on the specified path
    print_info "Running cloc on: $path"
    local output_file="$REPORTS_DIR/cloc_report_$(date +%Y%m%d_%H%M%S).txt"
    cloc "$path" --out="$output_file"
    cloc "$path"
    
    print_success "CLOC report saved to: $output_file"
}

# Simple cloc run (from scripts_03)
cloc_run() {
    local path="${1:-.}"
    if cmd_exists cloc; then
        cloc "$path"
    else
        print_error "cloc not installed"
        return 1
    fi
}

# ============================================================================
# FUNCTION COLLECTION FUNCTIONS (from scripts_02/collect_functions.sh)
# ============================================================================

# Function to use grep for collecting functions
grep_functions() {
    print_info "Collecting function names using grep..."
    grep -r "^def " . > ./functions.txt 2>/dev/null || true
    grep -r "^function " . >> ./functions.txt 2>/dev/null || true
    grep -r "^[[:space:]]*function " . >> ./functions.txt 2>/dev/null || true
    print_success "Function names collected using grep and saved to functions.txt"
}

# Function to use ctags for collecting functions
ctags_functions() {
    print_info "Collecting function names using ctags..."
    
    # Install ctags if it's not already installed
    if ! cmd_exists ctags; then
        print_info "Installing ctags..."
        if cmd_exists apt-get; then
            sudo apt-get update
            sudo apt-get install exuberant-ctags -y
        elif cmd_exists yum; then
            sudo yum install ctags -y
        elif cmd_exists brew; then
            brew install ctags
        else
            print_error "Cannot install ctags automatically. Please install it manually."
            return 1
        fi
    else
        print_success "ctags is already installed."
    fi
    
    ctags -R .
    grep "^[a-zA-Z0-9_]*$" tags | awk '{print $5, $1}' > ./functions.txt 2>/dev/null || true
    
    # Clean up temporary tags file
    rm -f tags
    
    print_success "Function names collected using ctags and saved to functions.txt"
}

# Function to use Python AST for collecting functions
ast_functions() {
    print_info "Collecting function names using Python AST..."
    
    # Check if Python is available
    if ! cmd_exists python && ! cmd_exists python3; then
        print_error "Python is not installed. Cannot use AST method."
        return 1
    fi
    
    # Determine Python command
    local python_cmd="python"
    if cmd_exists python3; then
        python_cmd="python3"
    fi
    
    # Create inline Python script for function extraction
    $python_cmd << 'EOF'
import ast
import os
import sys

def get_functions(filename):
    try:
        with open(filename, "r", encoding='utf-8', errors='ignore') as f:
            tree = ast.parse(f.read())
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(f"{filename}:{node.lineno}: def {node.name}")
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(f"{filename}:{node.lineno}: async def {node.name}")
            elif isinstance(node, ast.ClassDef):
                functions.append(f"{filename}:{node.lineno}: class {node.name}")
        return functions
    except (SyntaxError, UnicodeDecodeError, Exception) as e:
        print(f"Warning: Could not parse {filename}: {e}", file=sys.stderr)
        return []

def process_directory(directory):
    all_functions = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                all_functions.extend(get_functions(filepath))
    return all_functions

if __name__ == "__main__":
    functions = process_directory(".")
    if functions:
        with open("functions.txt", "w") as f:
            for func in functions:
                f.write(func + "\n")
        print(f"Found {len(functions)} Python functions/classes")
    else:
        print("No Python functions found")
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Function names collected using Python AST and saved to functions.txt"
    else
        print_error "Failed to extract functions using Python AST"
        return 1
    fi
}

# Interactive function collection
collect_functions_interactive() {
    print_header "Function Collection"
    
    echo "Choose a method to collect function names:"
    echo "1. grep (fast, basic pattern matching)"
    echo "2. ctags (comprehensive, requires ctags)"
    echo "3. Python AST (accurate for Python files)"
    echo "4. All methods combined"
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            grep_functions
            ;;
        2)
            ctags_functions
            ;;
        3)
            ast_functions
            ;;
        4)
            print_info "Running all function collection methods..."
            echo "=== GREP RESULTS ===" > functions_combined.txt
            grep_functions
            if [ -f "functions.txt" ]; then
                cat functions.txt >> functions_combined.txt
                echo "" >> functions_combined.txt
            fi
            
            echo "=== CTAGS RESULTS ===" >> functions_combined.txt
            ctags_functions
            if [ -f "functions.txt" ]; then
                cat functions.txt >> functions_combined.txt
                echo "" >> functions_combined.txt
            fi
            
            echo "=== PYTHON AST RESULTS ===" >> functions_combined.txt
            ast_functions
            if [ -f "functions.txt" ]; then
                cat functions.txt >> functions_combined.txt
            fi
            
            mv functions_combined.txt functions.txt
            print_success "All methods completed. Results combined in functions.txt"
            ;;
        *)
            print_error "Invalid choice. Please enter a number between 1 and 4."
            return 1
            ;;
    esac
}

# ============================================================================
# CODING ASSISTANT TOOLS (from scripts_03/coding_assistant_tools.sh)
# ============================================================================

# Install required tools
install_tools() {
    print_header "Installing Required Tools"
    
    local tools=("cloc" "ripgrep:rg" "shellcheck" "jq" "tree")
    for tool in "${tools[@]}"; do
        local cmd="${tool#*:}"
        cmd="${cmd:-$tool}"
        if ! cmd_exists "$cmd"; then
            print_info "Installing ${tool%:*}..."
            if cmd_exists apt-get; then
                apt-get update -qq && apt-get install -y "${tool%:*}"
            elif cmd_exists yum; then
                yum install -y "${tool%:*}"
            elif cmd_exists brew; then
                brew install "${tool%:*}"
            else
                print_warning "Cannot install ${tool%:*} automatically on this system"
            fi
        else
            print_success "${tool%:*} is already installed"
        fi
    done
}

# Search for patterns
search() {
    local pattern="${1:-TODO}"
    local path="${2:-.}"
    
    print_header "Pattern Search"
    print_info "Searching for pattern: '$pattern' in path: '$path'"
    
    if cmd_exists rg; then
        rg "$pattern" "$path" -n --with-filename
    elif cmd_exists grep; then
        grep -rn "$pattern" "$path"
    else
        print_error "No search tool available"
        return 1
    fi
}

# Lint shell scripts
lint_sh() {
    print_header "Shell Script Linting"
    
    if cmd_exists shellcheck; then
        find . -name "*.sh" -exec shellcheck {} +
    else
        print_error "shellcheck not installed"
        return 1
    fi
}

# Validate JSON files
lint_json() {
    print_header "JSON Validation"
    
    if cmd_exists jq; then
        find . -name "*.json" -exec sh -c 'jq -e . "$1" >/dev/null && echo "✅ $1" || echo "❌ $1"' _ {} +
    else
        print_error "jq not installed"
        return 1
    fi
}

# Git statistics
git_stats() {
    print_header "Git Statistics"
    
    if [[ ! -d .git ]]; then
        print_error "Not a git repository"
        return 1
    fi
    
    echo "Commits: $(git rev-list --count HEAD 2>/dev/null || echo 'N/A')"
    echo "Contributors:"
    git shortlog -sn | head -5 2>/dev/null || echo "None"
    echo ""
    echo "Recent commits:"
    git log --oneline -10 2>/dev/null || echo "None"
}

# Show directory tree
tree_show() {
    local depth="${1:-2}"
    
    print_header "Directory Tree (Depth: $depth)"
    
    if cmd_exists tree; then
        tree -L "$depth" -I '.git|node_modules|__pycache__|backups|reports'
    else
        find . -maxdepth "$depth" -type d | head -20
    fi
}

# Generate comprehensive report
generate_report() {
    local path="${1:-.}"
    local report_file="$REPORTS_DIR/full_report_$(date +%Y%m%d_%H%M%S).md"
    
    print_header "Generating Comprehensive Report"
    
    {
        echo "# Project Analysis Report"
        echo "Generated: $(date)"
        echo "Project: $(basename "$(realpath "$path")")"
        echo "Path: $(realpath "$path")"
        echo -e "\n## Code Metrics"
        cloc_run "$path" 2>/dev/null || echo "CLOC not available"
        echo -e "\n## Directory Structure\n\`\`\`"
        (cd "$path" && tree_show 3)
        echo -e "\`\`\`\n## Git Statistics"
        (cd "$path" && git_stats 2>/dev/null || echo "Not a git repository")
        echo -e "\n## File Summary"
        printf "- Shell scripts: %d\n" "$(find "$path" -name "*.sh" | wc -l)"
        printf "- JSON files: %d\n" "$(find "$path" -name "*.json" | wc -l)"
        printf "- Python files: %d\n" "$(find "$path" -name "*.py" | wc -l)"
        printf "- JavaScript files: %d\n" "$(find "$path" -name "*.js" | wc -l)"
        printf "- Markdown files: %d\n" "$(find "$path" -name "*.md" | wc -l)"
    } | tee "$report_file"
    
    print_success "Report generated: $report_file"
}

# ============================================================================
# FILE VERSIONING FUNCTIONS (from scripts_04/)
# ============================================================================

# Check if file should be ignored
should_ignore() {
    local file="$1"
    local ignore_file="$CURRENT_DIR/.versioningignore"
    
    # If .versioningignore doesn't exist, don't ignore anything
    if [ ! -f "$ignore_file" ]; then
        return 1
    fi
    
    # Get the relative path of the file from the watch directory
    local rel_path="${file#$CURRENT_DIR/}"
    
    # Check each pattern in .versioningignore
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        # Skip empty lines and comments
        [[ -z "$pattern" || "$pattern" =~ ^[[:space:]]*# ]] && continue
        
        # Trim whitespace
        pattern=$(echo "$pattern" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Convert glob pattern to regex
        regex=$(echo "$pattern" | sed 's/\./\\./g' | sed 's/\*/[^\/]*/g' | sed 's/\?/[^\/]/g')
        
        # If pattern ends with /, it's a directory pattern
        if [[ "$pattern" == */ ]]; then
            regex="^${regex}.*"
        else
            regex="^${regex}$"
        fi
        
        # Check if file matches the pattern
        if [[ "$rel_path" =~ $regex ]]; then
            return 0
        fi
    done < "$ignore_file"
    
    return 1
}

# Setup file versioning
setup_file_versioning() {
    print_header "Setting Up File Versioning"
    
    # Create default .versioningignore if it doesn't exist
    local versioning_ignore="$CURRENT_DIR/.versioningignore"
    if [ ! -f "$versioning_ignore" ]; then
        cat > "$versioning_ignore" << 'EOL'
# Default .versioningignore file
# Add patterns of files and directories to ignore during versioning

# System and temporary files
.DS_Store
*.tmp
*.temp
*.swp
*~
*cache.db*
.aider*
.file_versioning.pid*
.versioningignore*

# Common build and dependency directories
node_modules/
build/
dist/
target/
__pycache__/
*.pyc

# IDE and editor directories
.idea/
.vscode/
.settings/

# Log files
*.log
logs/

# Version control directories
.git/
.svn/

# Reports and backups
reports/
backups/

# Add your custom ignore patterns below this line
EOL
        print_success "Created default .versioningignore file at: $versioning_ignore"
    fi
    
    # Create backup directory
    mkdir -p "$BACKUPS_DIR"
    print_success "Backup directory created: $BACKUPS_DIR"
    
    # Update .gitignore
    local gitignore="$CURRENT_DIR/.gitignore"
    if [ ! -f "$gitignore" ]; then
        touch "$gitignore"
    fi
    
    # Add versioning-related entries to .gitignore
    local entries=("*.log" "*.pid" ".versioningignore" ".aider*" "*cache.db*" "backups/" "reports/")
    for entry in "${entries[@]}"; do
        if ! grep -q "^$entry$" "$gitignore" 2>/dev/null; then
            echo "$entry" >> "$gitignore"
        fi
    done
    
    print_success "Updated .gitignore with versioning entries"
}

# Start file versioning
start_file_versioning() {
    print_header "Starting File Versioning"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_warning "File versioning is already running (PID: $pid)"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Check for inotify-tools
    if ! cmd_exists inotifywait; then
        print_error "inotify-tools is not installed. Please install it first:"
        echo "Ubuntu/Debian: sudo apt-get install inotify-tools"
        echo "CentOS/RHEL: sudo yum install inotify-tools"
        return 1
    fi
    
    # Setup if not already done
    setup_file_versioning
    
    print_info "Starting file versioning system..."
    print_info "Watching directory: $CURRENT_DIR"
    print_info "Backup directory: $BACKUPS_DIR"
    
    # Start monitoring in background
    nohup bash -c "
        echo \$\$ > '$PID_FILE'
        trap 'rm -f $PID_FILE' EXIT
        
        inotifywait -m -r -e close_write '$CURRENT_DIR' --format '%w%f' | while read FILE
        do
            # Skip the backup directory itself and script files
            if [[ \"\$FILE\" == *\"/backups/\"* ]] || [[ \"\$FILE\" == *\"/reports/\"* ]] || [[ \"\$FILE\" == *\"run.sh\"* ]]; then
                continue
            fi
            
            # Check if file should be ignored based on .versioningignore
            if should_ignore \"\$FILE\"; then
                continue
            fi
            
            TIMESTAMP=\$(date +%Y_%m_%d_%H:%M:%S)
            BACKUP_FILE='$BACKUPS_DIR/\$(basename \"\$FILE\")_\$TIMESTAMP'
            cp \"\$FILE\" \"\$BACKUP_FILE\"
            echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Backup created: \$BACKUP_FILE\"
        done
    " > file_versioning.log 2>&1 &
    
    sleep 2  # Give it time to start
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        print_success "File versioning started successfully (PID: $pid)"
        print_info "Log file: file_versioning.log"
    else
        print_error "Failed to start file versioning"
        return 1
    fi
}

# Stop file versioning
stop_file_versioning() {
    print_header "Stopping File Versioning"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            rm -f "$PID_FILE"
            print_success "File versioning stopped (PID: $pid)"
        else
            rm -f "$PID_FILE"
            print_warning "File versioning was not running (stale PID file removed)"
        fi
    else
        print_warning "File versioning is not running"
    fi
    
    # Also kill any remaining inotifywait processes
    pkill -f "inotifywait.*$CURRENT_DIR" 2>/dev/null || true
}

# Check file versioning status
check_versioning() {
    print_header "File Versioning Status"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_success "File versioning is running"
            echo "  - PID: $pid"
            echo "  - Watching directory: $CURRENT_DIR"
            echo "  - Backup directory: $BACKUPS_DIR"
            echo "  - Log file: file_versioning.log"
            
            # Show recent backups
            if [ -d "$BACKUPS_DIR" ] && [ "$(ls -A "$BACKUPS_DIR" 2>/dev/null)" ]; then
                echo "  - Recent backups:"
                ls -lt "$BACKUPS_DIR" | head -5 | tail -n +2 | while read -r line; do
                    echo "    $line"
                done
            fi
        else
            rm -f "$PID_FILE"
            print_error "File versioning is not running (stale PID file removed)"
        fi
    else
        print_error "File versioning is not running"
    fi
}

# ============================================================================
# MAIN MENU SYSTEM
# ============================================================================

# Show main menu
show_main_menu() {
    clear
    print_color "$PURPLE" "
╔══════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE SHELL RUNNER               ║
║                  All Repository Functions                   ║
╚══════════════════════════════════════════════════════════════╝
"
    
    print_color "$CYAN" "📊 PROJECT ANALYSIS & INFORMATION"
    echo "  1)  Generate Project Information"
    echo "  2)  Count Lines of Code (CLOC)"
    echo "  3)  Collect Function Names"
    echo "  4)  Generate Comprehensive Report"
    echo ""
    
    print_color "$CYAN" "🔍 CODE SEARCH & ANALYSIS"
    echo "  5)  Search for Patterns"
    echo "  6)  Show Directory Tree"
    echo "  7)  Git Statistics"
    echo ""
    
    print_color "$CYAN" "✅ CODE QUALITY & LINTING"
    echo "  8)  Lint Shell Scripts"
    echo "  9)  Validate JSON Files"
    echo ""
    
    print_color "$CYAN" "🔄 FILE VERSIONING SYSTEM"
    echo "  10) Setup File Versioning"
    echo "  11) Start File Versioning"
    echo "  12) Stop File Versioning"
    echo "  13) Check Versioning Status"
    echo ""
    
    print_color "$CYAN" "🛠️  SYSTEM & UTILITIES"
    echo "  14) Install Required Tools"
    echo "  15) View Reports Directory"
    echo "  16) Clean Temporary Files"
    echo ""
    
    print_color "$CYAN" "📋 HELP & INFO"
    echo "  17) Show Help"
    echo "  18) About This Script"
    echo ""
    
    print_color "$RED" "  0)  Exit"
    echo ""
}

# Show help
show_help() {
    print_header "Help & Usage Information"
    
    cat << 'EOF'
This comprehensive shell script combines all functions from the repository's shell scripts:

SCRIPT SOURCES:
- scripts_01/00_generate_project_info.sh: Project analysis and information gathering
- scripts_01/cloc.sh & scripts_02/run_cloc.sh: Code line counting
- scripts_02/collect_functions.sh: Function name extraction
- scripts_03/coding_assistant_tools.sh: Development tools and utilities
- scripts_04/: File versioning system with inotify

MAIN FEATURES:
1. Project Information: Generates comprehensive project structure, line counts, and security scans
2. Code Analysis: CLOC integration for detailed code metrics
3. Function Collection: Extract function names using grep, ctags, or inline Python AST
4. Pattern Search: Fast text search using ripgrep or grep
5. Code Quality: Shell script linting and JSON validation
6. Git Integration: Repository statistics and contributor information
7. File Versioning: Automatic backup system using inotify
8. Report Generation: Timestamped reports in Markdown format

COMMAND LINE USAGE:
./run.sh [command] [options]

Available commands:
- project-info [path]     - Generate project information
- cloc [path]            - Count lines of code
- search [pattern] [path] - Search for patterns
- tree [depth]           - Show directory tree
- git-stats              - Show git statistics
- lint-sh                - Lint shell scripts
- lint-json              - Validate JSON files
- start-versioning       - Start file versioning
- stop-versioning        - Stop file versioning
- check-versioning       - Check versioning status
- install-tools          - Install required tools
- report [path]          - Generate comprehensive report

INTERACTIVE MODE:
Run without arguments for the interactive menu system.

REPORTS:
All reports are saved in the 'reports/' directory with timestamps.
File backups are stored in the 'backups/' directory.

DEPENDENCIES:
Optional tools that enhance functionality:
- cloc: Code metrics
- ripgrep (rg): Fast pattern searching
- tree: Directory visualization
- shellcheck: Shell script linting
- jq: JSON validation
- inotify-tools: File system monitoring
- ctags: Function extraction

EOF
}

# Show about information
show_about() {
    print_header "About This Script"
    
    cat << EOF
Comprehensive Shell Script Runner
Version: 1.0
Generated: $(date)

This script consolidates all shell script functions from the repository into a single,
interactive tool. It combines functionality from multiple script directories:

📁 scripts_01/: AI-powered scripting tools and project information generation
📁 scripts_02/: Function collection and code analysis utilities  
📁 scripts_03/: Coding assistant tools with comprehensive reporting
📁 scripts_04/: File versioning system with inotify monitoring

The script provides both interactive menu-driven operation and command-line interface
for automation and scripting purposes.

Features:
✅ Project structure analysis and documentation
✅ Code metrics and line counting
✅ Function name extraction and cataloging
✅ Pattern searching and code navigation
✅ Code quality checking and validation
✅ Git repository statistics and analysis
✅ Automatic file versioning and backup
✅ Comprehensive report generation
✅ Cross-platform compatibility

Author: Auto-generated from repository scripts
License: MIT (inherited from source scripts)
EOF
}

# View reports directory
view_reports() {
    print_header "Reports Directory"
    
    if [ -d "$REPORTS_DIR" ] && [ "$(ls -A "$REPORTS_DIR" 2>/dev/null)" ]; then
        print_info "Reports directory: $REPORTS_DIR"
        echo ""
        ls -la "$REPORTS_DIR"
        echo ""
        print_info "Total reports: $(ls -1 "$REPORTS_DIR" | wc -l)"
    else
        print_warning "No reports found in: $REPORTS_DIR"
    fi
    
    if [ -d "$BACKUPS_DIR" ] && [ "$(ls -A "$BACKUPS_DIR" 2>/dev/null)" ]; then
        echo ""
        print_info "Backups directory: $BACKUPS_DIR"
        echo ""
        ls -la "$BACKUPS_DIR" | head -10
        echo ""
        print_info "Total backups: $(ls -1 "$BACKUPS_DIR" | wc -l)"
    fi
}

# Clean temporary files
clean_temp_files() {
    print_header "Cleaning Temporary Files"
    
    local files_to_clean=("$REPORTS_DIR/project_structure.txt" "$REPORTS_DIR/sensitive_info.txt" "$REPORTS_DIR/line_counts.txt" "$REPORTS_DIR/project_info.txt" "functions.txt" "tags" "cloc_report.txt")
    local cleaned=0
    
    for file in "${files_to_clean[@]}"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            print_success "Removed: $file"
            ((cleaned++))
        fi
    done
    
    # Clean old log files
    find . -name "*.log" -mtime +7 -delete 2>/dev/null && print_success "Removed old log files"
    
    if [ $cleaned -eq 0 ]; then
        print_info "No temporary files to clean"
    else
        print_success "Cleaned $cleaned temporary files"
    fi
}

# Main interactive loop
main_loop() {
    while true; do
        show_main_menu
        read -rp "$(print_color "$WHITE" "Enter your choice (0-18): ")" choice
        echo
        
        case $choice in
            1)
                read -rp "Path to analyze [current directory]: " path
                generate_project_info "${path:-.}"
                ;;
            2)
                read -rp "Path to analyze [current directory]: " path
                install_and_run_cloc "${path:-.}"
                ;;
            3)
                collect_functions_interactive
                ;;
            4)
                read -rp "Path to analyze [current directory]: " path
                generate_report "${path:-.}"
                ;;
            5)
                read -rp "Pattern to search [TODO]: " pattern
                read -rp "Path to search [current directory]: " path
                search "${pattern:-TODO}" "${path:-.}"
                ;;
            6)
                read -rp "Tree depth [2]: " depth
                tree_show "${depth:-2}"
                ;;
            7)
                git_stats
                ;;
            8)
                lint_sh
                ;;
            9)
                lint_json
                ;;
            10)
                setup_file_versioning
                ;;
            11)
                start_file_versioning
                ;;
            12)
                stop_file_versioning
                ;;
            13)
                check_versioning
                ;;
            14)
                install_tools
                ;;
            15)
                view_reports
                ;;
            16)
                clean_temp_files
                ;;
            17)
                show_help
                ;;
            18)
                show_about
                ;;
            0)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter a number between 0 and 18."
                ;;
        esac
        
        echo
        read -rp "Press Enter to continue..."
    done
}

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

# Handle command line arguments
if [[ $# -eq 0 ]]; then
    # No arguments - run interactive mode
    main_loop
else
    # Command line mode
    case "$1" in
        project-info)
            generate_project_info "$2"
            ;;
        cloc)
            install_and_run_cloc "$2"
            ;;
        search)
            search "$2" "$3"
            ;;
        tree)
            tree_show "$2"
            ;;
        git-stats)
            git_stats
            ;;
        lint-sh)
            lint_sh
            ;;
        lint-json)
            lint_json
            ;;
        start-versioning)
            start_file_versioning
            ;;
        stop-versioning)
            stop_file_versioning
            ;;
        check-versioning)
            check_versioning
            ;;
        install-tools)
            install_tools
            ;;
        report)
            generate_report "$2"
            ;;
        collect-functions)
            collect_functions_interactive
            ;;
        help|--help|-h)
            show_help
            ;;
        about|--about)
            show_about
            ;;
        clean)
            clean_temp_files
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            print_info "Usage: $0 {command} [options]"
            echo ""
            print_info "Available commands:"
            echo "  project-info [path]     - Generate project information"
            echo "  cloc [path]            - Count lines of code"
            echo "  search [pattern] [path] - Search for patterns"
            echo "  tree [depth]           - Show directory tree"
            echo "  git-stats              - Show git statistics"
            echo "  lint-sh                - Lint shell scripts"
            echo "  lint-json              - Validate JSON files"
            echo "  start-versioning       - Start file versioning"
            echo "  stop-versioning        - Stop file versioning"
            echo "  check-versioning       - Check versioning status"
            echo "  install-tools          - Install required tools"
            echo "  report [path]          - Generate comprehensive report"
            echo "  collect-functions      - Collect function names"
            echo "  clean                  - Clean temporary files"
            echo "  help                   - Show help information"
            echo "  about                  - Show about information"
            echo ""
            print_info "Run without arguments for interactive menu."
            exit 1
            ;;
    esac
fi