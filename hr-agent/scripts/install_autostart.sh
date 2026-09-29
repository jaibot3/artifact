#!/bin/bash
# Jay Job Matcher — 맥 로그인 시 분석 서버 자동 실행 설정
# 사용법: bash scripts/install_autostart.sh
set -e

LABEL="com.jay.jobmatcher"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/jay-job-matcher.log"
PY="$(command -v python3 || true)"

if [ -z "$PY" ]; then echo "python3를 찾을 수 없어요."; exit 1; fi

echo "Anthropic API 키를 붙여넣고 Enter (입력해도 화면에 안 보이는 게 정상):"
read -rs KEY
echo
if [[ "$KEY" != sk-ant-* ]]; then echo "키 형식이 이상해요 (sk-ant- 로 시작해야 함). 중단합니다."; exit 1; fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
lsof -ti:8765 | xargs kill 2>/dev/null || true

cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$DIR/server.py</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>EnvironmentVariables</key><dict>
    <key>ANTHROPIC_API_KEY</key><string>$KEY</string>
    <key>PYTHONUNBUFFERED</key><string>1</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict></plist>
PL
chmod 600 "$PLIST"   # 키가 들어있으니 본인만 읽기 가능

launchctl bootstrap "gui/$(id -u)" "$PLIST"
sleep 2
if curl -s http://127.0.0.1:8765/health | grep -q '"ok": true'; then
  echo "✅ 완료. 서버가 켜졌고, 앞으로 맥 로그인할 때마다 자동으로 켜집니다."
  echo "   기록 차트: http://127.0.0.1:8765/history"
else
  echo "⚠️ 서버 응답이 없어요. 로그 확인: tail -30 $LOG"
fi
