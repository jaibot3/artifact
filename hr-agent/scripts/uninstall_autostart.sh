#!/bin/bash
# 자동 실행 해제 (키가 담긴 설정 파일도 삭제)
LABEL="com.jay.jobmatcher"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "자동 실행을 해제했어요."
