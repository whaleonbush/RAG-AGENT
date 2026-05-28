# GitHub Push 안내

로컬 커밋은 준비되어 있습니다. **인증만** 하면 push 됩니다.

## 방법 A — SSH (권장, 1회만)

1. 공개키 복사:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   (또는 이미 클립보드에 복사됨: `pbcopy < ~/.ssh/id_ed25519.pub`)

2. https://github.com/settings/ssh/new  
   - Title: `MacBook`  
   - Key: 붙여넣기 → **Add SSH key**

3. 확인 & push:
   ```bash
   ssh -T git@github.com
   cd /Users/kangtaeuk/Documents/cursor/260526_plm
   git remote set-url origin git@github.com:whaleonbush/RAG-AGENT.git
   bash scripts/push_to_github.sh
   ```

## 방법 B — GitHub CLI (브라우저 로그인)

```bash
gh auth login
# GitHub.com → HTTPS → Login with a web browser

cd /Users/kangtaeuk/Documents/cursor/260526_plm
bash scripts/push_to_github.sh
```

## 방법 C — PAT (토큰)

1. https://github.com/settings/tokens → Generate (`repo` 권한)  
2. **채팅에 토큰 붙이지 말 것**
   ```bash
   export GITHUB_TOKEN='여기에_새_토큰'
   git remote set-url origin "https://whaleonbush:${GITHUB_TOKEN}@github.com/whaleonbush/RAG-AGENT.git"
   git push -u origin main
   unset GITHUB_TOKEN
   ```

## 현재 SSH 공개키 (참고)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHwlP08eWlaL9WcX+YunWKx1UMOe2bDilkNbD8B9sB+I ceoistu@gmail.com
```

## 성공 확인

https://github.com/whaleonbush/RAG-AGENT 에 README, src/, docs/ 가 보이면 완료.
