# Virtual Environment - Quick Reference Card

## 🚀 One-Line Setup

### macOS/Linux
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Windows (CMD)
```cmd
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv venv; venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

---

## 📋 Common Commands

| Action | macOS/Linux | Windows |
|--------|-------------|---------|
| **Create venv** | `python3 -m venv venv` | `python -m venv venv` |
| **Activate** | `source venv/bin/activate` | `venv\Scripts\activate` |
| **Deactivate** | `deactivate` | `deactivate` |
| **Install deps** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **Check Python** | `which python` | `where python` |
| **List packages** | `pip list` | `pip list` |
| **Delete venv** | `rm -rf venv` | `rmdir /s venv` |

---

## ✅ Quick Checklist

- [ ] Virtual environment created: `ls venv/` or `dir venv`
- [ ] Activated: See `(venv)` in terminal prompt
- [ ] Dependencies installed: `pip list` shows streamlit, boto3, etc.
- [ ] Using venv Python: `which python` shows venv path

---

## 🔧 Automated Setup

### Use Setup Scripts (Easiest!)

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

These scripts will:
- ✅ Create virtual environment
- ✅ Activate it
- ✅ Install all dependencies
- ✅ Show next steps

---

## 🐛 Quick Troubleshooting

### Problem: "command not found: python3"
**Solution:** Use `python` instead of `python3`

### Problem: PowerShell script execution error
**Solution:** 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Virtual environment not activating
**Solution:** Recreate it
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Problem: Wrong packages installed
**Solution:** Check you're in venv
```bash
which python  # Should show venv/bin/python
pip list      # Should show project packages
```

---

## 💡 Pro Tips

### Tip 1: Create an alias
Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias vact='source venv/bin/activate'
```
Then just run: `vact`

### Tip 2: Auto-activate on cd
Add to `~/.bashrc` or `~/.zshrc`:
```bash
cd() {
  builtin cd "$@"
  if [[ -f venv/bin/activate ]]; then
    source venv/bin/activate
  fi
}
```

### Tip 3: Check if in venv
```bash
if [[ "$VIRTUAL_ENV" != "" ]]; then
  echo "In virtual environment: $VIRTUAL_ENV"
else
  echo "Not in virtual environment"
fi
```

### Tip 4: VS Code integration
VS Code auto-detects `venv/` - just select it as your interpreter:
- `Cmd+Shift+P` → "Python: Select Interpreter"
- Choose `./venv/bin/python`

---

## 📚 Full Documentation

For detailed instructions, see:
- **[VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)** - Complete guide with troubleshooting
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[README_STREAMLIT.md](README_STREAMLIT.md)** - Full application docs

---

## 🎯 Typical Workflow

```bash
# 1. Navigate to project
cd finops-genai-agent

# 2. Activate venv
source venv/bin/activate

# 3. Work on project
streamlit run streamlit_app.py
# or
python generate_sample_data.py

# 4. When done
deactivate
```

---

## 🆘 Still Having Issues?

1. **Read the full guide:** [VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)
2. **Check Python version:** `python --version` (need 3.8+)
3. **Recreate environment:** Delete `venv/` and start over
4. **Open an issue:** https://github.com/bgandhi001/finops-genai-agent/issues

---

**Remember:** Always activate the virtual environment before running the app! 🎯
