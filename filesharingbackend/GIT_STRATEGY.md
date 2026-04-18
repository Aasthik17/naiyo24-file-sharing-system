# Git Branching Strategy — FileShareSystem

## Branch Structure

```
main          ← production only, protected
└── dev       ← integration branch (dono devs yahan merge karenge)
    ├── feature/auth          (Dev A — Day 2)
    ├── feature/storage       (Dev B — Day 2-3)
    ├── feature/upload        (Dev A — Day 4-5)
    ├── feature/redis-session (Dev B — Day 4-5)
    ├── feature/share         (Dev A — Day 6)
    ├── feature/download      (Dev B — Day 6)
    ├── feature/celery        (Dev A — Day 7)
    └── feature/devops        (Dev B — Day 7)
```

## Daily Workflow

```bash
# 1. Subah sab se pehle dev se latest pull karo
git checkout dev
git pull origin dev

# 2. Apni feature branch banao
git checkout -b feature/your-feature-name

# 3. Kaam karo, commits karo
git add .
git commit -m "feat: description of what you did"

# 4. Push karo
git push origin feature/your-feature-name

# 5. GitHub pe Pull Request banao → dev mein merge
```

## Commit Message Format

```
feat: naya feature add kiya
fix: bug fix
refactor: code restructure
test: tests add kiye
docs: documentation update
chore: config/setup changes
```

## Rules

- **main mein directly push mat karo**
- **PR banate waqt dusre dev se review lo** (even 5 min quick review)
- **Har din shaam dev mein merge karo** taaki conflicts na badhen
- `.env` file **kabhi commit mat karo** — `.gitignore` mein hai

## First Time Setup

```bash
git clone <repo-url>
cd filesharesystem
cp backend/.env.example backend/.env   # apni values bharo
docker compose up -d --build
```
