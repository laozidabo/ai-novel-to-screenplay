#!/bin/bash
# wf-recorder 录屏脚本 (Wayland 原生)
# Usage:
#   ./record_wf.sh                    # 录全屏, 无限时长, Ctrl+C 停止
#   ./record_wf.sh with-audio         # 全屏 + 系统音频
#
# 注: wf-recorder 不支持 -t 限时, 只能 Ctrl+C 手动停止
#     定时录制用: timeout 30 ./record_wf.sh
#     或:        timeout 60 ./record_wf.sh with-audio

AUDIO_FLAG=""
for arg in "$@"; do
    case "$arg" in
        with-audio) AUDIO_FLAG="--audio" ;;
    esac
done

OUT="$(date +%Y%m%d_%H%M%S)_demo.mkv"
echo "===================="
echo "🎬 wf-recorder 录屏 (Wayland)"
echo "===================="
echo "输出: $OUT"
echo "音频: ${AUDIO_FLAG:+是} ${AUDIO_FLAG:-否}"
echo "停止: Ctrl+C"
echo "===================="

wf-recorder -f "$OUT" $AUDIO_FLAG

echo ""
echo "✅ 录制完成: $OUT"
ls -lh "$OUT"
echo ""
echo "转 mp4: ffmpeg -i $OUT -c:v libx264 -crf 23 -preset medium ${OUT%.mkv}.mp4"
