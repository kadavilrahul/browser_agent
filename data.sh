#!/bin/bash

# Streamlined Data Analysis Script
# Generates reports for any specified directory
set -e

# Colors
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' B='\033[0;34m' C='\033[0;36m' NC='\033[0m'

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Utility functions
msg() { echo -e "${2:-$G}$1$NC"; }
err() { msg "$1" "$R"; }
warn() { msg "$1" "$Y"; }
info() { msg "$1" "$B"; }
cmd_exists() { command -v "$1" &>/dev/null; }

# Open reports folder in file manager
open_reports_folder() {
    if cmd_exists xdg-open; then
        xdg-open "$REPORTS_DIR" 2>/dev/null &
        info "Reports folder opened in file manager"
    elif cmd_exists open; then
        open "$REPORTS_DIR" 2>/dev/null &
        info "Reports folder opened in Finder"
    elif cmd_exists explorer; then
        explorer "$REPORTS_DIR" 2>/dev/null &
        info "Reports folder opened in Explorer"
    else
        warn "Cannot open file manager automatically"
        info "Please manually navigate to: $REPORTS_DIR"
    fi
}

# Interactive folder selection
select_folder() {
    local dirs=()
    local i=0
    
    # Build directory list
    dirs[0]="."
    ((i++))
    
    # Add parent directory option if not at root
    if [ "$(pwd)" != "/" ]; then
        dirs[$i]=".."
        ((i++))
    fi
    
    # Add subdirectories
    for dir in */; do
        if [ -d "$dir" ] && [[ "$dir" != "reports/" ]] && [[ ! "$dir" =~ ^\. ]]; then
            dirs[$i]="${dir%/}"
            ((i++))
        fi
    done
    
    # Display options to stderr so they don't interfere with return value
    {
        echo ""
        msg "Directory Selection - Current: $(pwd)" "$C"
        echo "  0) Current directory (.)"
        
        local j=1
        if [ "$(pwd)" != "/" ]; then
            echo "  1) Parent directory (..)"
            j=2
        fi
        
        for ((k=j; k<i; k++)); do
            echo "  $k) ${dirs[$k]}"
        done
        
        echo ""
        echo "Options:"
        echo "  • Enter a number to select from the list above"
        echo "  • Enter an absolute path (e.g., /home/user/project)"
        echo "  • Enter a relative path (e.g., ../other-project)"
        echo "  • Type 'browse' to navigate step by step"
        echo "  • Type 'home' for home directory ($HOME)"
        echo "  • Type 'root' for root directory (/)"
        echo ""
    } >&2
    
    read -p "Select directory or enter path: " choice >&2
    
    # Handle special commands
    case "$choice" in
        "browse")
            browse_directories
            return $?
            ;;
        "home")
            echo "$HOME"
            return 0
            ;;
        "root")
            echo "/"
            return 0
            ;;
    esac
    
    # Return selected directory to stdout
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 0 ] && [ "$choice" -lt "$i" ]; then
        echo "${dirs[$choice]}"
    elif [ -d "$choice" ]; then
        echo "$(cd "$choice" && pwd)"  # Return absolute path
    else
        err "Invalid selection or directory doesn't exist: $choice" >&2
        return 1
    fi
}

# Interactive directory browser
browse_directories() {
    local current_dir="$(pwd)"
    
    while true; do
        {
            echo ""
            msg "Directory Browser - Current: $(pwd)" "$C"
            echo ""
            
            local dirs=()
            local i=0
            
            # Add current directory option
            dirs[0]="."
            echo "  0) Select current directory"
            ((i++))
            
            # Add parent directory if not at root
            if [ "$(pwd)" != "/" ]; then
                dirs[$i]=".."
                echo "  1) Go to parent directory (..)"
                ((i++))
            fi
            
            # Add subdirectories
            for dir in */; do
                if [ -d "$dir" ] && [[ ! "$dir" =~ ^\. ]]; then
                    dirs[$i]="${dir%/}"
                    echo "  $i) Enter ${dir%/}/"
                    ((i++))
                fi
            done
            
            echo ""
            echo "Commands: 'q' to quit browser, 'h' for home directory"
            echo ""
        } >&2
        
        read -p "Choose option: " choice >&2
        
        case "$choice" in
            "q"|"quit")
                cd "$current_dir"
                return 1
                ;;
            "h"|"home")
                cd "$HOME"
                ;;
            *)
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 0 ] && [ "$choice" -lt "$i" ]; then
                    if [ "$choice" -eq 0 ]; then
                        # Select current directory
                        echo "$(pwd)"
                        return 0
                    else
                        # Navigate to selected directory
                        local target="${dirs[$choice]}"
                        if [ -d "$target" ]; then
                            cd "$target" || {
                                err "Cannot access directory: $target" >&2
                                continue
                            }
                        fi
                    fi
                else
                    err "Invalid choice: $choice" >&2
                fi
                ;;
        esac
    done
}

# Project structure generation
generate_tree() {
    local dir="$1"
    if cmd_exists tree; then
        tree "$dir" -I '.git|node_modules|__pycache__|venv|.venv|dist|build|*.pyc|*.log'
    else
        find "$dir" -type f -not -path '*/.*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' | head -50
    fi
}

# Generate project information
generate_project_info() {
    local directory="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="$REPORTS_DIR/project_report_$timestamp.md"
    
    info "Analyzing: $(cd "$directory" && pwd)"
    
    {
        echo "# Project Analysis Report"
        echo "Generated: $(date)"
        echo "Directory: $(cd "$directory" && pwd)"
        echo ""
        
        echo "## Project Structure"
        echo '```'
        generate_tree "$directory"
        echo '```'
        echo ""
        
        echo "## Security Scan"
        if grep -r -i --exclude-dir=".git" --exclude-dir="node_modules" \
           -E "(API_KEY|SECRET|PASSWORD|TOKEN)" "$directory" 2>/dev/null | head -10; then
            echo "⚠️ Potential sensitive data found"
        else
            echo "✅ No sensitive patterns detected"
        fi
        echo ""
        
        echo "## Code Statistics"
        local total=0 count=0
        for ext in py js ts sh java go rb php html css json; do
            local files=$(find "$directory" -name "*.$ext" -not -path '*/.*' -not -path '*/node_modules/*' 2>/dev/null | wc -l)
            local lines=$(find "$directory" -name "*.$ext" -not -path '*/.*' -not -path '*/node_modules/*' -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)
            if [ "$files" -gt 0 ]; then
                echo "- $ext files: $files ($lines lines)"
                total=$((total + lines))
                count=$((count + files))
            fi
        done
        echo ""
        echo "**Total: $count files, $total lines**"
        
    } > "$report_file"
    
    msg "Report saved: $report_file"
    msg "Reports directory: $REPORTS_DIR" "$C"
    
    # Display the report contents immediately
    echo ""
    msg "📄 Report Contents:" "$C"
    echo ""
    cat "$report_file"
    
    # Open reports folder
    echo ""
    info "Opening reports folder..."
    open_reports_folder
}

# CLOC function
run_cloc() {
    local path="$1"
    if cmd_exists cloc; then
        info "Running CLOC on: $path"
        local cloc_file="$REPORTS_DIR/cloc_$(date +%Y%m%d_%H%M%S).txt"
        cloc "$path" --out="$cloc_file"
        cloc "$path"
        
        echo ""
        msg "CLOC report saved: $cloc_file"
        msg "Reports directory: $REPORTS_DIR" "$C"
        info "Opening reports folder..."
        open_reports_folder
    else
        warn "CLOC not installed. Install with: sudo apt install cloc"
        return 1
    fi
}

# Function collection
collect_functions() {
    local path="$1"
    local output="$REPORTS_DIR/functions_$(date +%Y%m%d_%H%M%S).txt"
    
    info "Collecting functions from: $path"
    {
        echo "# Functions found in $path"
        echo "Generated: $(date)"
        echo ""
        
        # Python functions
        find "$path" -name "*.py" -exec grep -H "^def \|^class " {} \; 2>/dev/null | head -50
        
        # JavaScript functions  
        find "$path" -name "*.js" -exec grep -H "function \|const.*=.*=>" {} \; 2>/dev/null | head -20
        
        # Shell functions
        find "$path" -name "*.sh" -exec grep -H "^[a-zA-Z_][a-zA-Z0-9_]*(" {} \; 2>/dev/null | head -20
        
    } > "$output"
    
    msg "Functions saved: $output"
    msg "Reports directory: $REPORTS_DIR" "$C"
    
    # Display the functions file contents
    echo ""
    msg "📄 Functions Contents:" "$C"
    echo ""
    cat "$output"
    
    # Open reports folder
    echo ""
    info "Opening reports folder..."
    open_reports_folder
}

# Search patterns
search() {
    local pattern="$1"
    local path="$2"
    
    info "Searching for '$pattern' in $path"
    if cmd_exists rg; then
        rg "$pattern" "$path" -n --with-filename | head -20
    else
        grep -rn "$pattern" "$path" 2>/dev/null | head -20
    fi
}

# Git statistics
git_stats() {
    local path="$1"
    local original_dir=$(pwd)
    cd "$path" || return 1
    
    if [[ ! -d .git ]]; then
        warn "Not a git repository"
        cd "$original_dir"
        return 1
    fi
    
    echo "Commits: $(git rev-list --count HEAD 2>/dev/null)"
    echo "Contributors: $(git shortlog -sn | wc -l)"
    echo "Recent commits:"
    git log --oneline -5 2>/dev/null
    cd "$original_dir"
}

# Show help
show_help() {
    echo "Usage: $0 [directory] [command]"
    echo ""
    echo "Commands:"
    echo "  report     - Generate project analysis report"
    echo "  cloc       - Run CLOC code counter"
    echo "  functions  - Extract function definitions"
    echo "  search     - Search for patterns"
    echo "  git        - Show git statistics"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/project report"
    echo "  $0 . search TODO"
    echo "  $0 version_01 cloc"
}

# Main execution
main() {
    local target_dir=""
    local cmd=""
    local pattern=""
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        # No arguments - interactive mode
        msg "Data Analysis Script" "$C"
        target_dir=$(select_folder)
        if [ $? -ne 0 ]; then
            exit 1
        fi
        
        echo ""
        msg "Available commands:" "$C"
        echo "  1) report     - Generate project analysis report"
        echo "  2) cloc       - Run CLOC code counter"
        echo "  3) functions  - Extract function definitions"
        echo "  4) search     - Search for patterns"
        echo "  5) git        - Show git statistics"
        echo ""
        read -p "Select command (1-5): " choice
        
        case "$choice" in
            1) cmd="report" ;;
            2) cmd="cloc" ;;
            3) cmd="functions" ;;
            4) cmd="search"
               read -p "Enter search pattern [TODO]: " pattern
               pattern="${pattern:-TODO}" ;;
            5) cmd="git" ;;
            *) err "Invalid choice"; exit 1 ;;
        esac
        
    elif [ -d "$1" ]; then
        # First arg is directory
        target_dir="$1"
        cmd="${2:-report}"
        pattern="$3"
    else
        # First arg is command
        cmd="$1"
        if [ "$cmd" = "help" ] || [ "$cmd" = "-h" ] || [ "$cmd" = "--help" ]; then
            show_help
            return
        fi
        target_dir=$(select_folder)
        if [ $? -ne 0 ]; then
            exit 1
        fi
        if [ "$cmd" = "search" ]; then
            read -p "Enter search pattern [TODO]: " pattern >&2
            pattern="${pattern:-TODO}"
        fi
    fi
    
    # Execute command
    case "$cmd" in
        "report"|"info")
            generate_project_info "$target_dir"
            ;;
        "cloc")
            run_cloc "$target_dir"
            ;;
        "functions")
            collect_functions "$target_dir"
            ;;
        "search")
            pattern="${pattern:-TODO}"
            search "$pattern" "$target_dir"
            ;;
        "git")
            git_stats "$target_dir"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            err "Unknown command: $cmd"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"