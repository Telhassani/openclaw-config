## Plan: Backup Config + Skills to GitHub

### Files to Include

| Item | Path | Notes |
|------|------|-------|
| Core config | `SOUL.md`, `IDENTITY.md`, `USER.md` | Your persona |
| Agent config | `AGENTS.md`, `MEMORY.md`, `HEARTBEAT.md` | Agent behavior |
| Skills | `.agents/skills/` | 6 skills (~324KB total) |
| Memory logs | `memory/` | Daily notes |
| Scripts | `scripts/` | Your custom scripts |
| Skill lock | `skills-lock.json` | Skill versions |
| Setup script | `setup.sh` | Bootstrap for fresh installs |

### Files to Exclude (`.gitignore`)

```
# Secrets
credentials.json
google-credentials.json
*.rdb

# Local
.openclaw/
.pi/
__pycache__/
*.pyc
test.txt
dump.rdb
```

---

### Commit Message Conventions

| Change Type | When | Example Message |
|-------------|------|-----------------|
| **Config changes** | After editing SOUL.md, USER.md, AGENTS.md | `Update identity settings` |
| **Skills added/removed** | After installing/removing skills | `Add obsidian-bases skill` |
| **Memory** | Daily or weekly | `Memory update: 2026-03-02` |

---

### Steps

1. **Create `.gitignore`** — exclude secrets  
2. **Create `setup.sh`** — bootstrap script for restores  
3. **Initialize git** — `git init`, first commit  
4. **Create GitHub repo** — `openclaw-config` via `gh` CLI or browser  
5. **Push** — `git remote add`, `git push`  

---

### Restore Workflow

```bash
# After updating OpenClaw
git pull origin main
./setup.sh
openclaw gateway restart
```

---

### Ongoing Workflow

```bash
# Check what changed
git status

# For config changes
git add SOUL.md USER.md AGENTS.md
git commit -m "Update identity settings"
git push origin main

# For skills
git add .agents/skills/ skills-lock.json
git commit -m "Add obsidian-bases skill"
git push origin main

# For memory
git add memory/
git commit -m "Memory update: 2026-03-02"
git push origin main
```

---

### Alias (optional)

```bash
# Add to ~/.bashrc/~/.zshrc
alias gp="cd /data/.openclaw/workspace && git add . && git commit -m 'Update' && git push origin main"
```
