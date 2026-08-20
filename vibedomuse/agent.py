# -*- coding: utf-8 -*-
"""
VibeDoMuse · agent.py
Agent orchestration layer. Exposes several entry points:
  - run()             rule engine: natural language -> rule-parsed params -> template
                      search -> rule composition -> render (default / fallback)
  - run_llm()         LLM + knowledge base: natural language -> knowledge retrieval
                      (spec + templates) -> LLM writes JSON -> local validation -> render
  - run_variants()    generate N seed variants of a request (rule engine)
  - run_layers()      generate calm/tense layer variants of the same theme
  - parse_only(text)  parse-only preview
"""
import time
import random
from . import nl_parser as nlp
from . import template_db as tdb
from . import generator as gen
from . import renderer as rnd
from . import llm_client as llm
from .nl_parser import MusicParams


def _refine(text, use_llm):
    """Optional: rewrite the request text with the local model; None on failure."""
    if not use_llm:
        return None
    try:
        return llm.refine_intent(text) or None
    except Exception:
        return None


def parse_only(text, seed=None, use_llm=False):
    llm_text = _refine(text, use_llm)
    if llm_text:
        text = llm_text
    params = nlp.parse(text, seed=seed)
    return {
        "text": text,
        "llm_text": llm_text,
        "params": params.__dict__,
        "summary": params.summary(),
    }


def run(text, use_template=None, seed=None, limit_templates=5, use_llm=False):
    """Full rule-engine pipeline. Returns structured result (params, matched
    templates, generated score and audio)."""
    t0 = time.time()
    if seed is None:
        seed = random.randint(0, 1_000_000)
    llm_text = _refine(text, use_llm)
    if llm_text:
        text = llm_text
    params = nlp.parse(text, seed=seed)

    # 1) template search: let the Agent find the most relevant templates
    templates = tdb.search(params, limit=limit_templates)

    # 2) compose a new piece (based on parsed params)
    if use_template:
        base = tdb.get_by_name(use_template)
        if base:
            # render the template's JSON directly (all three batches, including
            # bgm which has no pre-rendered WAV)
            rendered = rnd.render_existing_json(base["path"], base["name"])
            return _finalize(params, templates, None, rendered, t0, seed, use_template, llm_text)
    score = gen.compose(params, seed=seed)
    name = gen.slug(params) + "_" + str(seed % 100000)
    rendered = rnd.render(score, name)

    return _finalize(params, templates, score, rendered, t0, seed, None, llm_text)


def run_variants(text, n=4, seed=None, limit_templates=5, use_llm=False):
    """Generate n rule-engine variants of the same request (different seeds).

    Returns a list of results, each shaped like run()'s result.
    """
    if seed is None:
        seed = random.randint(0, 1_000_000)
    llm_text = _refine(text, use_llm)
    if llm_text:
        text = llm_text
    params = nlp.parse(text, seed=seed)
    templates = tdb.search(params, limit=limit_templates)
    out = []
    for i in range(max(1, int(n))):
        t0 = time.time()
        s = (seed + i * 7919) % 1_000_000
        score = gen.compose(params, seed=s)
        name = gen.slug(params) + "_" + str(s % 100000)
        rendered = rnd.render(score, name)
        res = _finalize(params, templates, score, rendered, t0, s, None, llm_text)
        res["variant"] = i + 1
        res["variants_total"] = n
        out.append(res)
    return out


def run_layers(text, seed=None, limit_templates=5, use_llm=False):
    """Generate calm/tense layer variants of the same theme.

    Returns a dict {ok, summary, layers: [{layer, label, result}], params...}.
    """
    t0 = time.time()
    if seed is None:
        seed = random.randint(0, 1_000_000)
    llm_text = _refine(text, use_llm)
    if llm_text:
        text = llm_text
    params = nlp.parse(text, seed=seed)
    templates = tdb.search(params, limit=limit_templates)
    layers = []
    for item in gen.gen_layers(params, seed=seed):
        lt0 = time.time()
        score = item["score"]
        name = gen.slug(params) + "_" + item["layer"] + "_" + str(seed % 100000)
        rendered = rnd.render(score, name)
        res = _finalize(params, templates, score, rendered, lt0, seed, None, llm_text)
        res["layer"] = item["layer"]
        res["layer_label"] = item["label"]
        layers.append(res)
    return {
        "ok": True,
        "text": params.text,
        "params": params.__dict__,
        "summary": params.summary(),
        "seed": seed,
        "elapsed_sec": round(time.time() - t0, 2),
        "layers": layers,
        "method": "layers",
    }


def run_llm(text, use_template=None, seed=None, limit_templates=5, top_examples=1):
    """LLM + knowledge-base pipeline: knowledge retrieval -> LLM writes JSON
    -> local validation -> render.

    Any failure (no LLM response / unparseable JSON / validation failure /
    render failure) gracefully falls back to the rule engine.
    Returns a result shaped like run()'s, plus method / knowledge_* / llm_* info.
    """
    from . import knowledge as kb
    from . import json_writer as jw
    from . import json_validator as jv

    t0 = time.time()
    if seed is None:
        seed = random.randint(0, 1_000_000)

    # ① knowledge retrieval (spec excerpts + template examples)
    prompt = kb.build_prompt(text, top_sections=3, top_examples=top_examples)
    sec_titles = [s["title"] for s in prompt["sections"]]
    ex_names = [r["name"] for r in prompt["templates"]]

    # ② LLM writes JSON
    score, err = jw.write_score(text, prompt=prompt)
    if score is None:
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = err or "LLM 无输出"
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    # ③ local validation
    ok, errors, warnings = jv.validate(score)
    if not ok:
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = "本地校验失败: " + "; ".join(errors[:5])
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    score = jv.normalize(score)
    # honor user intent for seamless loop (LLM may not know the extension field)
    try:
        p0 = nlp.parse(text)
        if p0.loop:
            score.setdefault("loop", True)
    except Exception:
        pass
    params = jv.to_params(score)
    params.text = text
    templates = tdb.search(params, limit=limit_templates)
    name = "llm_" + gen.slug(params) + "_" + str(seed % 100000)
    try:
        rendered = rnd.render(score, name)
    except Exception as e:  # noqa: BLE001
        # render failure (e.g. DoMuse cannot parse) -> fall back to the rule engine
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = "LLM JSON 渲染失败: " + str(e)
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    res = _finalize(params, templates, score, rendered, t0, seed, None, method="llm")
    res["llm_warnings"] = warnings
    res["knowledge_sections"] = sec_titles
    res["knowledge_examples"] = ex_names
    return res


def _finalize(params, templates, score, rendered, t0, seed, use_template, llm_text=None, method="rule"):
    category_cn = {
        "galgame_bgm": "旋律驱动 BGM",
        "galgame_accompaniment": "和声驱动伴奏",
        "galgame_v3": "多调性三轨",
    }.get(params.category, params.category)
    return {
        "ok": True,
        "text": params.text,
        "params": params.__dict__,
        "summary": params.summary(),
        "category_cn": category_cn,
        "templates": templates,
        "used_template": use_template,
        "generated": rendered,
        "score": score,
        "elapsed_sec": round(time.time() - t0, 2),
        "seed": seed,
        "llm_text": llm_text,
        "llm_refined": bool(llm_text),
        "method": method,
    }
