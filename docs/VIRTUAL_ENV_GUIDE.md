# Virtual Environment Setup Guide

## Why Use a Virtual Environment?

Virtual environments isolate your project dependencies from your system Python, preventing:
- Dependency conflicts between projects
- Accidental system Python modifications
- Version incompatibilities
- Permission issues

## Quick Setup

### macOS / Linux

```bash
# Navigate to project directory
cd finops-genai-agent

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# When done, deactivate
deactivate
```

### Windows (Command Prompt)

```cmd
# Navigate to project directory
cd finops-genai-agent

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Your prompt should now show (venv)
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# When done, deactivate
deactivate
```

### Windows (PowerShell)

```powershell
# Navigate to project directory
cd finops-genai-agent

# Create virtual environment
python -m venv venv

# Activate it (may need to enable script execution first)
venv\Scripts\Activate.ps1

# If you get an error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Your prompt should now show (venv)
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# When done, deactivate
deactivate
```

## Detailed Instructions

### 1. Create Virtual Environment

The virtual environment creates an isolated Python installation in a folder called `venv`:

```bash
python3 -m venv venv
```

**What this does:**
- Creates a `venv/` directory
- Copies Python interpreter
- Creates isolated `site-packages/` for dependencies
- Sets up activation scripts

**Options:**
```bash
# Use specific Python version
python3.11 -m venv venv

# Create with system site packages (not recommended)
python3 -m venv --system-site-packages venv

# Create in different location
python3 -m venv ~/my-envs/finops-env
```

### 2. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash (Windows):**
```bash
source venv/Scripts/activate
```

**How to verify it's activated:**
- Your prompt shows `(venv)` prefix
- `which python` shows path to `venv/bin/python`
- `pip list` shows only minimal packages

```bash
# Check Python location
which python
# Should show: /path/to/finops-genai-agent/venv/bin/python

# Check pip location
which pip
# Should show: /path/to/finops-genai-agent/venv/bin/pip
```

### 3. Install Dependencies

With the virtual environment activated:

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list

# Should see:
# streamlit, pandas, boto3, plotly, etc.
```

### 4. Run Your Application

```bash
# Make sure (venv) is in your prompt
streamlit run streamlit_app.py
```

### 5. Deactivate When Done

```bash
deactivate
```

This returns you to your system Python.

## Common Issues & Solutions

### Issue 1: "python3: command not found"

**Solution:**
```bash
# Try just 'python'
python -m venv venv

# Or install Python 3
# macOS:
brew install python3

# Ubuntu/Debian:
sudo apt-get install python3 python3-venv

# Windows: Download from python.org
```

### Issue 2: "venv module not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# Or use virtualenv instead
pip install virtualenv
virtualenv venv
```

### Issue 3: PowerShell Execution Policy Error

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
venv\Scripts\Activate.ps1
```

### Issue 4: Permission Denied (macOS/Linux)

**Solution:**
```bash
# Make activation script executable
chmod +x venv/bin/activate

# Then activate
source venv/bin/activate
```

### Issue 5: Virtual Environment Not Activating

**Check:**
```bash
# Verify venv directory exists
ls venv/

# Should see: bin/ (or Scripts/ on Windows), lib/, etc.

# If missing, recreate it
rm -rf venv
python3 -m venv venv
```

### Issue 6: Wrong Python Version

**Solution:**
```bash
# Specify exact Python version
python3.11 -m venv venv

# Or use pyenv to manage Python versions
pyenv install 3.11
pyenv local 3.11
python -m venv venv
```

## IDE Integration

### VS Code

1. Open project folder
2. VS Code should auto-detect `venv/`
3. Select interpreter: `Cmd+Shift+P` → "Python: Select Interpreter"
4. Choose `./venv/bin/python`

**Or manually:**

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `venv/bin/python`

### Jupyter Notebook

```bash
# Activate venv first
source venv/bin/activate

# Install ipykernel
pip install ipykernel

# Add venv as Jupyter kernel
python -m ipykernel install --user --name=finops-venv

# Launch Jupyter
jupyter notebook

# Select "finops-venv" kernel in notebook
```

## Best Practices

### 1. Always Activate Before Working

```bash
# Add to your workflow
cd finops-genai-agent
source venv/bin/activate
# Now you can run commands
```

### 2. Keep requirements.txt Updated

```bash
# After installing new packages
pip freeze > requirements.txt

# Or manually edit requirements.txt
```

### 3. Don't Commit venv/ to Git

Already in `.gitignore`:
```
venv/
ENV/
env/
```

### 4. Use Different Environments for Different Projects

```bash
# Project 1
cd project1
python3 -m venv venv
source venv/bin/activate

# Project 2
cd ../project2
python3 -m venv venv
source venv/bin/activate
```

### 5. Document Python Version

Add to README:
```markdown
## Requirements
- Python 3.11+
```

Or use `.python-version` file:
```bash
echo "3.11" > .python-version
```

## Alternative Tools

### 1. virtualenv (Classic)

```bash
# Install
pip install virtualenv

# Create environment
virtualenv venv

# Activate (same as venv)
source venv/bin/activate
```

### 2. conda (Data Science)

```bash
# Create environment
conda create -n finops python=3.11

# Activate
conda activate finops

# Install dependencies
conda install streamlit pandas boto3 plotly

# Deactivate
conda deactivate
```

### 3. pipenv (Modern)

```bash
# Install
pip install pipenv

# Create environment and install dependencies
pipenv install -r requirements.txt

# Activate
pipenv shell

# Run command without activating
pipenv run streamlit run streamlit_app.py
```

### 4. poetry (Advanced)

```bash
# Install
curl -sSL https://install.python-poetry.org | python3 -

# Initialize (if starting fresh)
poetry init

# Install dependencies
poetry install

# Run command
poetry run streamlit run streamlit_app.py
```

## Quick Reference

### Common Commands

```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Install packages
pip install package-name
pip install -r requirements.txt

# List installed packages
pip list
pip freeze

# Update package
pip install --upgrade package-name

# Uninstall package
pip uninstall package-name

# Deactivate
deactivate

# Delete environment
rm -rf venv                           # macOS/Linux
rmdir /s venv                         # Windows
```

### Environment Variables

```bash
# Set in activated environment
export AWS_REGION=us-east-1           # macOS/Linux
set AWS_REGION=us-east-1              # Windows

# Or use .env file (recommended)
cp .env.example .env
# Edit .env with your values
```

## Troubleshooting Checklist

- [ ] Virtual environment created: `ls venv/`
- [ ] Virtual environment activated: `(venv)` in prompt
- [ ] Using venv Python: `which python` shows venv path
- [ ] Dependencies installed: `pip list` shows packages
- [ ] Correct Python version: `python --version`
- [ ] AWS credentials configured: `aws sts get-caller-identity`
- [ ] Environment variables set: `echo $AWS_REGION`

## Getting Help

If you're still having issues:

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Recreate environment:**
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check for conflicts:**
   ```bash
   pip check
   ```

4. **Use verbose mode:**
   ```bash
   pip install -v -r requirements.txt
   ```

5. **Open an issue:**
   - GitHub: https://github.com/bgandhi001/finops-genai-agent/issues
   - Include: OS, Python version, error message

---

**Pro Tip**: Add this alias to your shell config for quick activation:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias vact='source venv/bin/activate'

# Then just run:
vact
```
