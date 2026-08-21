# -*- coding: utf-8 -*-
"""
VibeDoMuse · frontend_pyqt6/i18n.py
Lightweight translation layer (English / Chinese) extracted from main.py so
that workers / dialogs / widgets can reuse it without importing the main window.
"""
from vibedomuse import config as _cfg

_LANG = None  # cached after first call


def _lang():
    global _LANG
    if _LANG is None:
        _LANG = _cfg.get_language()
    return _LANG


def _reload_lang():
    global _LANG
    _LANG = _cfg.get_language()


_T = {
    # Window / title
    "VibeDoMuse · AI Music Agent": "VibeDoMuse · AI 音乐创作 Agent",
    "VibeDoMuse · AI Music Agent (Natural Language → Knowledge Base → Score Generation)":
        "VibeDoMuse · AI 音乐创作 Agent（自然语言 → 知识库 → 乐谱生成）",

    # Menu — File
    "File": "文件",
    "Exit": "退出",

    # Menu — Theme
    "Theme": "主题",
    "Light": "浅色",
    "Dark": "暗色",

    # Menu — Settings
    "Settings": "设置",
    "LLM Settings": "LLM 设置",
    "Language": "语言",
    "English": "English",
    "Chinese": "中文",

    # Menu — Tools
    "Tools": "工具",
    "Template Browser (144 pieces)": "模板库浏览器（144 首）",
    "Mix Adjustment\u2026": "混音调整\u2026",

    # Left panel
    "Natural Language Description": "自然语言描述",
    "Placeholder_Example": "例如：来一首忧伤的 a 小调慢速钢琴曲\n"
                           "例如：我想要一首温柔的 C 大调钢琴伴奏，琶音风格，90 速度\n"
                           "例如：生成一段忧伤的 Dm 小调戏剧性三轨弦乐铺垫，脉冲织体\n"
                           "提示：加「循环」生成无缝循环 BGM；加「鼓」添加打击乐轨",
    "Modify / Follow-up Input": "修改 / 追问输入",
    "Modify_Followup_Placeholder": "修改 / 追问：在此输入修改意见或追问，再点击「生成歌曲」\n"
                                   "例如：把副歌加快、加亮，主歌再轻一些\n"
                                   "或者：这段为什么用了 Dm 调？能换成更明亮的调吗？",
    "Generate Song": "生成歌曲",
    "Re-generate (same seed)": "同种子再生成",
    "Change Seed Variant": "换种子变体",
    "Layer Variation": "分层变奏",
    "Batch Variants\u2026": "批量变体\u2026",
    "Export\u2026": "导出\u2026",
    "Export Format": "导出格式",
    "All Files (*)": "所有文件 (*)",

    # Tabs
    "JSON Preview": "JSON 预览",
    "Piano Roll": "钢琴卷帘",
    "Log": "日志",

    # Player
    "Play": "试听",
    "Stop": "停止",
    "Loop": "循环",
    "Not generated yet": "尚未生成",
    "Loop playback: seamless background music loop": "循环播放：无缝循环 BGM 模式",

    # Status bar
    "KB items": "KB 项",
    "templates": "个模板",
    "Creating\u2026": "创作中\u2026",
    "Ready. Enter a description and click Generate.": "就绪。输入描述后点击生成歌曲。",

    # LLM Settings dialog
    "LLM Settings (plaintext in root config.ini)": "LLM 设置（明文存于根目录 config.ini）",
    "API Base URL": "API Base URL",
    "Model Name": "模型名称",
    "API Key": "API Key",
    "Timeout (s)": "超时(秒)",
    "Temperature": "温度",
    "Higher values make the model more creative/random. Lower values make it more deterministic. (0.0 - 2.0)":
        "值越高模型越随机/有创意，值越低越确定（0.0 - 2.0）",
    "Test Connection": "测试连接",
    "Save": "保存",
    "Cancel": "取消",
    "Connection OK": "连接成功",
    "Connection failed": "连接失败",
    "OK": "确定",
    "Settings saved. Restart required for some changes to take effect.":
        "设置已保存。部分更改需重启后生效。",

    # Template Browser dialog
    "Template Browser": "模板浏览器",
    "Filter\u2026": "过滤\u2026",
    "Preview": "预览",
    "Close": "关闭",
    "Filter templates by keyword\u2026": "按关键词过滤模板\u2026",
    "tracks": "音轨",
    "Generate from this template": "以该模板为基础生成",
    "No templates match.": "无匹配模板。",

    # Mix dialog
    "Mix Adjustment": "混音调整",
    "No score loaded yet.": "尚未加载乐谱。",
    "Mute": "静音",
    "Apply & Re-render": "应用并重新渲染",
    "Mix": "混音",
    "Volume": "音量",

    # Understanding dialog
    "Confirm AI Understanding": "确认 AI 理解",
    "The AI understands your request as follows. Confirm to proceed, or modify the description.":
        "AI 对您的请求理解如下。确认后继续生成，或修改描述。",
    "You can modify the understanding above before confirming.":
        "您可以在确认前修改上面的理解内容。",
    "If correct, click": "如果正确，点击",
    "to proceed, or click": "继续生成，或点击",
    "to go back.": "返回修改。",
    "Confirm & Generate": "确认并生成",
    "Modify Description": "修改描述",

    # Connection test
    "Test Result": "测试结果",
    "Connection successful!": "连接成功！",
    "Connection failed!": "连接失败！",
    "Model responded:": "模型响应：",
    "Details:": "详情：",
    "Saved": "已保存",
    "Configuration saved to:": "配置已保存到：",
    "Test Connection": "测试连接",

    # Status messages
    "Generation failed": "生成失败",
    "Error:": "错误：",
    "Remix completed": "混音后重新渲染完成",
    "Seed:": "随机种子：",
    "Ready:": "就绪：",
    "Playing...": "播放中...",
    "Stopped:": "已停止：",
    "Export Complete": "导出完成",
    "Export Error": "导出错误",
    "Playback": "播放",
    "No audio available. Please generate a song first.": "没有可用的音频。请先生成一首歌曲。",

    # Generation status
    "Analysis complete\u2026": "分析完成\u2026",
    "Generating\u2026": "生成中\u2026",
    "Generated": "已生成",
    "Error": "错误",
    "Parse Preview": "解析预览",
    "Please enter a natural language description first.": "请先输入自然语言描述。",
    "Please generate a song first before exporting.": "请先生成歌曲，再导出。",
    "How many variants (2-8)?": "生成几个变体（2-8）？",

    # Log
    "LOG_CLEAR": "清除日志",
    "LOG_PREVIEW": "预览",
    "LOG_UNDERSTANDING": "AI 理解分析",
    "LOG_GENERATION": "生成",

    # Follow-up
    "Follow-up": "追问",
    "User Feedback": "用户反馈",
    "Your feedback on the generated music": "对生成音乐的反馈",
    "Generate Follow-up": "生成追问",
    "Enter your feedback to improve the music": "输入反馈以改进音乐",
    "Follow-up Generation": "追问生成",

    # History
    "History": "历史记录",
    "View Details": "查看详情",
    "User Request": "用户请求",
    "AI Understanding": "AI 理解",
    "Generated JSON": "生成的 JSON",
    "Timestamp": "时间戳",
    "Seed": "随机种子",
    "Method": "生成方式",
    "Feedback": "反馈",
    "No history yet": "暂无历史记录",
    "History Details": "历史记录详情",
    "Original Request": "原始请求",
    "Initial Understanding": "初始理解",
    "Follow-up Conversation": "追问对话",
    "Copy JSON": "复制 JSON",
    "Load this result": "加载此结果",
    "Conversation Thread": "对话线程",
}


def _(key):
    """Translate an English UI string to the current language.

    Returns the English string by default; returns the Chinese translation
    when the language is set to 'zh'.
    """
    if _lang() == "zh":
        return _T.get(key, key)
    return key


def set_language(lang):
    """Change the UI language at runtime."""
    _cfg.set_language(lang)
    _reload_lang()
