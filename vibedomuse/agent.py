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
import logging
import time
import random
from . import nl_parser as nlp
from . import template_db as tdb
from . import generator as gen
from . import renderer as rnd
from . import llm_client as llm
from .nl_parser import MusicParams

log = logging.getLogger(__name__)

# Constants
MAX_SEED = 1_000_000  # Maximum value for random seed generation
VARIANT_MULTIPLIER = 7919  # Multiplier for generating seed variants (prime number)


def _refine(text, use_llm):
    """Optional: rewrite the request text with the local model; None on failure."""
    if not use_llm:
        return None
    try:
        return llm.refine_intent(text) or None
    except Exception as e:  # noqa: BLE001
        log.warning("LLM intent refinement failed (falling back to raw text): %s", e)
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
        seed = random.randint(0, MAX_SEED)
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
        seed = random.randint(0, MAX_SEED)
    llm_text = _refine(text, use_llm)
    if llm_text:
        text = llm_text
    params = nlp.parse(text, seed=seed)
    templates = tdb.search(params, limit=limit_templates)
    out = []
    for i in range(max(1, int(n))):
        t0 = time.time()
        s = (seed + i * VARIANT_MULTIPLIER) % MAX_SEED
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
        seed = random.randint(0, MAX_SEED)
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


def run_llm(text, use_template=None, seed=None, limit_templates=5, top_examples=1, on_token=None):
    """LLM + knowledge-base pipeline: knowledge retrieval -> LLM writes JSON
    -> local validation -> render.

    Any failure (no LLM response / unparseable JSON / validation failure /
    render failure) gracefully falls back to the rule engine.
    Returns a result shaped like run()'s, plus method / knowledge_* / llm_* info.

    ``on_token`` (optional callable) receives each streamed LLM text chunk as it
    arrives (enables real-time UI streaming); it does not affect the result.
    """
    from . import knowledge as kb
    from . import json_writer as jw
    from . import json_validator as jv

    t0 = time.time()
    if seed is None:
        seed = random.randint(0, MAX_SEED)

    # ① knowledge retrieval (spec excerpts + template examples)
    prompt = kb.build_prompt(text, top_sections=3, top_examples=top_examples)
    sec_titles = [s["title"] for s in prompt["sections"]]
    ex_names = [r["name"] for r in prompt["templates"]]

    # ② LLM writes JSON
    score, err = jw.write_score(text, prompt=prompt, on_token=on_token)
    if score is None:
        log.warning("run_llm: LLM JSON write failed (%s); falling back to rule engine", err)
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = err or "LLM no output"
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    # ③ local validation
    ok, errors, warnings = jv.validate(score)
    if not ok:
        log.warning("run_llm: local validation failed (%s); falling back to rule engine",
                    "; ".join(errors[:5]))
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = "Local validation failed: " + "; ".join(errors[:5])
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    score = jv.normalize(score)
    # honor user intent for seamless loop (LLM may not know the extension field)
    try:
        p0 = nlp.parse(text)
        if p0.loop:
            score.setdefault("loop", True)
    except Exception as e:  # noqa: BLE001
        log.warning("run_llm: could not parse user text for loop intent: %s", e)
    params = jv.to_params(score)
    params.text = text
    templates = tdb.search(params, limit=limit_templates)
    name = "llm_" + gen.slug(params) + "_" + str(seed % 100000)
    try:
        rendered = rnd.render(score, name)
    except Exception as e:  # noqa: BLE001
        # render failure (e.g. DoMuse cannot parse) -> fall back to the rule engine
        log.warning("run_llm: render failed (%s); falling back to rule engine", e)
        res = run(text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "fallback"
        res["llm_error"] = "LLM JSON render failed: " + str(e)
        res["knowledge_sections"] = sec_titles
        res["knowledge_examples"] = ex_names
        return res

    res = _finalize(params, templates, score, rendered, t0, seed, None, method="llm")
    res["llm_warnings"] = warnings
    res["knowledge_sections"] = sec_titles
    res["knowledge_examples"] = ex_names
    return res


def analyze(text, on_token=None):
    """First-stage: send the user's prompt to LLM for intent analysis.

    The LLM autonomously considers which parts of the knowledge base are
    relevant and returns a natural-language understanding paragraph.
    Returns the analysis text, or None on failure.
    """
    from . import llm_client as llm
    try:
        return llm.analyze_intent(text, on_token=on_token)
    except Exception as e:  # noqa: BLE001
        log.warning("LLM intent analysis failed: %s", e)
        return None


def run_llm_v2(text, analysis, seed=None, limit_templates=5, top_examples=1, on_token=None):
    """Second-stage: generate JSON with original prompt + LLM's understanding.

    Uses the original user prompt + the LLM's own intent analysis (from stage 1)
    to produce a more accurate JSON score. Falls back to standard run_llm on failure.
    """
    from . import json_writer as jw
    from . import json_validator as jv
    from . import knowledge as kb

    t0 = time.time()
    if seed is None:
        seed = random.randint(0, MAX_SEED)

    # ① Build combined prompt (original text + analysis + knowledge context)
    prompt = kb.build_generation_prompt(text, analysis, top_sections=3, top_examples=top_examples)
    sec_titles = [s["title"] for s in prompt["sections"]]
    ex_names = [r["name"] for r in prompt["templates"]]

    # ② LLM writes JSON using the combined prompt
    score, err = jw.write_score(text, prompt=prompt, on_token=on_token)
    if score is None:
        # fallback to standard run_llm
        log.warning("run_llm_v2: LLM JSON write failed (%s); falling back to run_llm", err)
        res = run_llm(text, seed=seed, limit_templates=limit_templates, top_examples=top_examples)
        res["method"] = "fallback_v2"
        res["llm_error"] = err or "LLM no output (v2)"
        res["v2_analysis"] = analysis
        return res

    # ③ local validation
    ok, errors, warnings = jv.validate(score)
    if not ok:
        log.warning("run_llm_v2: local validation failed (%s); falling back to run_llm",
                    "; ".join(errors[:5]))
        res = run_llm(text, seed=seed, limit_templates=limit_templates, top_examples=top_examples)
        res["method"] = "fallback_v2"
        res["llm_error"] = "Local validation failed (v2): " + "; ".join(errors[:5])
        res["v2_analysis"] = analysis
        return res

    score = jv.normalize(score)
    try:
        p0 = nlp.parse(text)
        if p0.loop:
            score.setdefault("loop", True)
    except (ValueError, KeyError, TypeError) as e:
        log.warning("run_llm_v2: could not parse user text for loop intent: %s", e)
    params = jv.to_params(score)
    params.text = text
    templates = tdb.search(params, limit=limit_templates)
    name = "llm_v2_" + gen.slug(params) + "_" + str(seed % 100000)
    try:
        rendered = rnd.render(score, name)
    except Exception as e:
        log.warning("run_llm_v2: render failed (%s); falling back to run_llm", e)
        res = run_llm(text, seed=seed, limit_templates=limit_templates, top_examples=top_examples)
        res["method"] = "fallback_v2"
        res["llm_error"] = "LLM JSON render failed (v2): " + str(e)
        res["v2_analysis"] = analysis
        return res

    res = _finalize(params, templates, score, rendered, t0, seed, None, method="llm_v2")
    res["llm_warnings"] = warnings
    res["knowledge_sections"] = sec_titles
    res["knowledge_examples"] = ex_names
    res["v2_analysis"] = analysis
    return res


def run_followup(original_text, original_analysis, current_score, user_feedback,
                  seed=None, limit_templates=5, top_examples=1, on_token=None):
    """Follow-up generation: modify the current score based on user feedback.

    Uses the original user prompt, initial understanding, current JSON score, and user's feedback
    to generate an improved version. Falls back to rule engine on LLM failure.

    Returns a result shaped like run_llm()'s, with additional followup context.
    """
    from . import json_writer as jw
    from . import json_validator as jv
    from . import knowledge as kb

    t0 = time.time()
    if seed is None:
        seed = random.randint(0, MAX_SEED)

    # Build follow-up prompt
    prompt = kb.build_followup_prompt(original_text, original_analysis, current_score, user_feedback,
                                     top_sections=3, top_examples=top_examples)
    sec_titles = [s["title"] for s in prompt["sections"]]
    ex_names = [r["name"] for r in prompt["templates"]]

    # LLM writes JSON using follow-up prompt
    score, err = jw.write_score(original_text, prompt=prompt, on_token=on_token)
    if score is None:
        log.warning("run_followup: LLM JSON write failed (%s); falling back to rule engine", err)
        res = run(original_text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "followup_fallback"
        res["followup_error"] = err or "LLM no output"
        res["followup_feedback"] = user_feedback
        return res

    # Local validation
    ok, errors, warnings = jv.validate(score)
    if not ok:
        log.warning("run_followup: local validation failed (%s); falling back to rule engine",
                    "; ".join(errors[:5]))
        res = run(original_text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "followup_fallback"
        res["followup_error"] = "Local validation failed: " + "; ".join(errors[:5])
        res["followup_feedback"] = user_feedback
        return res

    score = jv.normalize(score)
    # Preserve loop intent from original request
    _apply_loop_intent(score, original_text)

    params = jv.to_params(score)
    params.text = original_text
    templates = tdb.search(params, limit=limit_templates)
    name = "followup_" + gen.slug(params) + "_" + str(seed % 100000)
    try:
        rendered = rnd.render(score, name)
    except Exception as e:
        log.warning("run_followup: render failed (%s); falling back to rule engine", e)
        res = run(original_text, seed=seed, limit_templates=limit_templates, use_llm=False)
        res["method"] = "followup_fallback"
        res["followup_error"] = "LLM JSON render failed: " + str(e)
        res["followup_feedback"] = user_feedback
        return res

    res = _finalize(params, templates, score, rendered, t0, seed, None, method="followup")
    res["llm_warnings"] = warnings
    res["knowledge_sections"] = sec_titles
    res["knowledge_examples"] = ex_names
    res["original_analysis"] = original_analysis
    res["followup_feedback"] = user_feedback
    res["previous_score"] = current_score
    return res


def _apply_loop_intent(score, text):
    """Apply loop intent from user text to the score (common logic)."""
    try:
        p0 = nlp.parse(text)
        if p0.loop:
            score.setdefault("loop", True)
    except (ValueError, KeyError, TypeError) as e:
        log.warning("Could not parse user text for loop intent: %s", e)


def _finalize(params, templates, score, rendered, t0, seed, use_template, llm_text=None, method="rule"):
    category_cn = {
        "galgame_bgm": "Melody-driven BGM",
        "galgame_accompaniment": "Harmony-driven accompaniment",
        "galgame_v3": "Multi-tonal three-track",
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
