# -*- coding: utf-8 -*-
"""
VibeDoMuse · 开发态冒烟测试 (dev-mode smoke test)

验证在「源码态」下路径解析、模板/知识库加载、config.ini 自动创建、
二进制与声音字体解析是否正常。打包后用 windows/_smoke_frozen.py 在冻结环境复测。

用法 (在 venv 中):
    python build/_smoke.py
"""
import os
import sys
import traceback

# 让脚本可从项目根目录运行
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

failures = []


def check(name, cond, detail=""):
    status = "OK " if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  -> {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def main():
    from vibedomuse import config, knowledge, template_db, renderer, server

    # 1) 配置文件自动创建（源码态写入项目根 config.ini）
    cfg_initially = os.path.exists(config.CONFIG_PATH)
    # 触发创建/读取（首次运行 main 时 GUI 也会调用 ensure_config_file）
    try:
        config.ensure_config_file()
    except Exception as e:
        print("  config.ensure_config_file() raised:", e)
    cfg_exists = os.path.exists(config.CONFIG_PATH)
    check("config.ini 解析路径存在", os.path.isabs(config.CONFIG_PATH), config.CONFIG_PATH)
    check("config.ini 可被创建/读取", cfg_exists,
          f"初始存在={cfg_initially}, 创建后存在={cfg_exists}")

    # 2) 二进制与声音字体
    check("DoMuse.exe 解析存在", os.path.exists(renderer.DOMUSE_EXE), renderer.DOMUSE_EXE)
    check("fluidsynth.exe 解析存在", os.path.exists(renderer.FLUIDSYNTH_EXE), renderer.FLUIDSYNTH_EXE)
    check("32MbGMStereo.sf2 解析存在", os.path.exists(renderer.SOUNDFONT), renderer.SOUNDFONT)

    # 3) 格式说明书
    check("JSON_Format_Specification.md 解析存在",
          os.path.exists(knowledge.SPEC_PATH), knowledge.SPEC_PATH)

    # 4) 模板目录与统计
    for cat, d in template_db.CATALOG_DIRS.items():
        check(f"模板目录存在 [{cat}]", os.path.isdir(d), d)
    stats = template_db.stats()
    total = stats.get("total", 0)
    check("模板统计总数 > 0", total > 0, f"stats={stats}")

    # 5) 知识库检索（不联网，纯加载说明书 + TF-IDF）
    try:
        secs = knowledge.retrieve_sections("快乐 轻快 钢琴", top_k=1)
        check("知识库检索成功", isinstance(secs, list) and len(secs) >= 1,
              f"返回 {len(secs)} 段")
    except Exception as e:
        check("知识库检索成功", False, repr(e))
        traceback.print_exc()

    # 6) 运行时可写目录（源码态=项目根，冻结态=exe 所在目录）
    try:
        os.makedirs(renderer.RUNTIME_DIR, exist_ok=True)
        check("RUNTIME_DIR 可写", os.access(renderer.RUNTIME_DIR, os.W_OK), renderer.RUNTIME_DIR)
    except Exception as e:
        check("RUNTIME_DIR 可写", False, repr(e))

    # 7) server 生成目录创建（server.main 内会创建，这里直接验证可创建）
    try:
        os.makedirs(server.GEN_WAV_DIR, exist_ok=True)
        os.makedirs(server.GEN_JSON_DIR, exist_ok=True)
        check("server 生成目录已创建",
              os.path.isdir(server.GEN_WAV_DIR) and os.path.isdir(server.GEN_JSON_DIR),
              f"{server.GEN_WAV_DIR} / {server.GEN_JSON_DIR}")
    except Exception as e:
        check("server 生成目录已创建", False, repr(e))

    print()
    if failures:
        print(f"❌ 失败 {len(failures)} 项: {failures}")
        sys.exit(1)
    print("✅ 全部通过")


if __name__ == "__main__":
    main()
