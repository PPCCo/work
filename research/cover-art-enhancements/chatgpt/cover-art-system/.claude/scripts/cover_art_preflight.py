#!/usr/bin/env python3
"""Validate the structure and declared quality gates of a cover prompt package.

This checker is intentionally deterministic and dependency-free. It cannot assess
whether an image is beautiful or whether Qwen followed a prompt; Claude's independent
cover-art critique and visual review remain mandatory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_POLICY = SCRIPT_DIR.parent / "config" / "cover-art-policy.json"
PLACEHOLDER_RE = re.compile(
    r"\[(?:BOOK\s+)?(?:TITLE|SERIES\s+NAME|PUBLISHER\s+NAME|INSERT[^\]]*)\]"
    r"|\b(?:TODO|TBD|INSERT\s+TITLE|BOOK\s+TITLE\s+HERE|REPLACE\s+ME)\b",
    re.IGNORECASE,
)


class PackageValidationError(Exception):
    """Raised when package/policy files cannot be processed."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except OSError as exc:
        raise PackageValidationError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PackageValidationError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise PackageValidationError(f"Expected a JSON object at the root of {path}.")
    return value


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def add_missing_key_errors(
    obj: Any, required_keys: list[str], context: str, errors: list[str]
) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{context} must be a JSON object.")
        return
    missing = [key for key in required_keys if key not in obj]
    if missing:
        errors.append(f"{context} is missing required key(s): {', '.join(missing)}.")


def validate_package(package: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    package_policy = policy.get("package", {})
    review_policy = policy.get("review", {})
    text_policy = policy.get("text", {})
    mode_policy = policy.get("modes", {})
    generation_policy = policy.get("generation", {})

    add_missing_key_errors(
        package,
        package_policy.get("required_top_level_keys", []),
        "Package",
        errors,
    )

    if package.get("schema_version") != package_policy.get("schema_version"):
        errors.append(
            f"schema_version must be {package_policy.get('schema_version')!r}; "
            f"received {package.get('schema_version')!r}."
        )

    mode = package.get("mode")
    if mode not in ("brief", "reference_inspired"):
        errors.append("mode must be either 'brief' or 'reference_inspired'.")

    # Book identity and exact text contract.
    book = package.get("book")
    required_book_keys = package_policy.get("required_book_keys", [])
    add_missing_key_errors(book, required_book_keys, "book", errors)
    if not isinstance(book, dict):
        book = {}

    for key in (
        "project_id",
        "title",
        "publisher_name",
        "product_type",
        "audience",
        "book_summary",
        "cover_promise",
        "visual_thesis",
    ):
        if not non_empty_string(book.get(key)):
            errors.append(f"book.{key} must be a non-empty string.")

    for key in ("subtitle", "series_name"):
        if not isinstance(book.get(key), str):
            errors.append(f"book.{key} must be a string (use an empty string only when absent).")

    fmt = book.get("format")
    if not isinstance(fmt, dict):
        errors.append("book.format must be an object containing orientation and aspect_ratio.")
    else:
        for key in ("orientation", "aspect_ratio"):
            if not non_empty_string(fmt.get(key)):
                errors.append(f"book.format.{key} must be a non-empty string.")

    if not isinstance(book.get("assumptions"), list):
        errors.append("book.assumptions must be an array, even when empty.")

    text = book.get("text_to_render")
    text_keys = text_policy.get("required_fields", [])
    add_missing_key_errors(text, text_keys, "book.text_to_render", errors)
    if not isinstance(text, dict):
        text = {}

    for key in text_keys:
        if not isinstance(text.get(key), str):
            errors.append(f"book.text_to_render.{key} must be a string.")
    for key in ("title", "publisher_name"):
        if not non_empty_string(text.get(key)):
            errors.append(f"book.text_to_render.{key} must not be empty.")

    for text_key, book_key in (
        ("title", "title"),
        ("subtitle", "subtitle"),
        ("series_name", "series_name"),
        ("publisher_name", "publisher_name"),
    ):
        if isinstance(text.get(text_key), str) and isinstance(book.get(book_key), str):
            if text[text_key] != book[book_key]:
                errors.append(
                    f"book.text_to_render.{text_key} must exactly match book.{book_key}."
                )

    # Reference analysis contract.
    reference_analysis = package.get("reference_analysis")
    if not isinstance(reference_analysis, dict):
        errors.append("reference_analysis must be an object.")
        reference_analysis = {}
    references = reference_analysis.get("references")
    if not isinstance(references, list):
        errors.append("reference_analysis.references must be an array.")
        references = []
    if not non_empty_string(reference_analysis.get("synthesis")):
        errors.append("reference_analysis.synthesis must be a non-empty string.")

    reference_ids: list[str] = []
    for index, ref in enumerate(references, start=1):
        context = f"reference_analysis.references[{index - 1}]"
        if not isinstance(ref, dict):
            errors.append(f"{context} must be an object.")
            continue
        if not non_empty_string(ref.get("id")):
            errors.append(f"{context}.id must be a non-empty string.")
        else:
            reference_ids.append(ref["id"])
        if not isinstance(ref.get("design_principles"), list) or not ref.get("design_principles"):
            errors.append(f"{context}.design_principles must be a non-empty array.")
        if not isinstance(ref.get("avoid_copying"), list):
            errors.append(f"{context}.avoid_copying must be an array.")
        if not non_empty_string(ref.get("translation_for_book")):
            errors.append(f"{context}.translation_for_book must be a non-empty string.")
        if "filename" in ref and not isinstance(ref.get("filename"), str):
            errors.append(f"{context}.filename must be a string when provided.")
    if len(reference_ids) != len(set(reference_ids)):
        errors.append("reference_analysis.references contains duplicate reference IDs.")

    # Direction completeness and distinctness.
    directions = package.get("directions")
    required_direction_keys = package_policy.get("required_direction_keys", [])
    if not isinstance(directions, list):
        errors.append("directions must be an array.")
        directions = []
    if not directions:
        errors.append("directions must contain at least one direction.")

    direction_ids: list[str] = []
    concept_names: list[str] = []
    normalized_prompts: list[str] = []
    normalized_hooks: list[str] = []

    required_visible_strings: list[tuple[str, str]] = []
    for key, label in (
        ("title", "title"),
        ("subtitle", "subtitle"),
        ("series_name", "series name"),
        ("publisher_name", "publisher name"),
    ):
        value = text.get(key)
        if isinstance(value, str) and value.strip():
            required_visible_strings.append((value, label))

    for index, direction in enumerate(directions, start=1):
        context = f"directions[{index - 1}]"
        add_missing_key_errors(direction, required_direction_keys, context, errors)
        if not isinstance(direction, dict):
            continue

        direction_id = direction.get("id")
        if not non_empty_string(direction_id):
            errors.append(f"{context}.id must be a non-empty string.")
        else:
            direction_ids.append(direction_id)

        for key in (
            "concept_name",
            "reader_effect",
            "book_specific_rationale",
            "visual_hook",
            "focal_subject",
            "composition",
            "rendering_language",
            "typography_plan",
            "prompt",
            "distinctiveness_note",
        ):
            if not non_empty_string(direction.get(key)):
                errors.append(f"{context}.{key} must be a non-empty string.")

        if not isinstance(direction.get("palette"), list) or not direction.get("palette"):
            errors.append(f"{context}.palette must be a non-empty array of palette descriptions.")
        elif any(not non_empty_string(item) for item in direction.get("palette", [])):
            errors.append(f"{context}.palette items must all be non-empty strings.")

        if not isinstance(direction.get("negative_prompt"), str):
            errors.append(f"{context}.negative_prompt must be a string (empty is allowed).")

        prompt = direction.get("prompt", "")
        if isinstance(prompt, str):
            if PLACEHOLDER_RE.search(prompt):
                errors.append(f"{context}.prompt contains a likely unresolved placeholder.")
            for visible_text, label in required_visible_strings:
                if visible_text not in prompt:
                    errors.append(
                        f"{context}.prompt does not contain the exact required {label}: {visible_text!r}."
                    )
            normalized_prompts.append(re.sub(r"\s+", " ", prompt.strip().casefold()))
        concept = direction.get("concept_name", "")
        if isinstance(concept, str) and concept.strip():
            concept_names.append(re.sub(r"\s+", " ", concept.strip().casefold()))
        hook = direction.get("visual_hook", "")
        if isinstance(hook, str) and hook.strip():
            normalized_hooks.append(re.sub(r"\s+", " ", hook.strip().casefold()))

        ref_id = direction.get("reference_id")
        if mode == "brief" and ref_id is not None:
            errors.append(f"{context}.reference_id must be null in brief mode.")
        elif mode == "reference_inspired":
            if not non_empty_string(ref_id):
                errors.append(f"{context}.reference_id must identify its source reference in reference-inspired mode.")
            elif ref_id not in reference_ids:
                errors.append(f"{context}.reference_id {ref_id!r} does not exist in reference_analysis.references.")

    if len(direction_ids) != len(set(direction_ids)):
        errors.append("directions contains duplicate IDs.")
    if len(concept_names) != len(set(concept_names)):
        errors.append("directions contains duplicate concept_name values; concept directions must be distinct.")
    if len(normalized_prompts) != len(set(normalized_prompts)):
        errors.append("directions contains identical prompts; each direction must be materially distinct.")
    if len(normalized_hooks) != len(set(normalized_hooks)):
        warnings.append("Some directions repeat the same visual_hook; confirm that they differ conceptually, not only in palette.")

    if mode == "brief":
        minimum_directions = mode_policy.get("brief", {}).get("minimum_directions", 3)
        if len(directions) < minimum_directions:
            errors.append(f"brief mode requires at least {minimum_directions} directions; found {len(directions)}.")
        if references:
            errors.append("brief mode must use an empty reference_analysis.references array.")
    elif mode == "reference_inspired":
        minimum_references = mode_policy.get("reference_inspired", {}).get("minimum_references", 1)
        if len(references) < minimum_references:
            errors.append(f"reference-inspired mode requires at least {minimum_references} reference image(s).")
        if len(directions) != len(references):
            errors.append(
                f"reference-inspired mode requires one direction per supplied reference: "
                f"{len(references)} reference(s), {len(directions)} direction(s)."
            )
        direction_ref_ids = [
            direction.get("reference_id") for direction in directions if isinstance(direction, dict)
        ]
        if len(direction_ref_ids) == len(references):
            if set(direction_ref_ids) != set(reference_ids):
                errors.append("Every reference must map to exactly one direction, with no missing or repeated reference IDs.")

    # Critic scorecard and independent gate.
    review = package.get("critic_review")
    if not isinstance(review, dict):
        errors.append("critic_review must be an object.")
        review = {}
    ratings = review.get("ratings")
    if not isinstance(ratings, list):
        errors.append("critic_review.ratings must be an array.")
        ratings = []

    weights = review_policy.get("dimension_weights", {})
    required_dimensions = list(weights.keys())
    critical_dimensions = review_policy.get("critical_dimensions", [])
    score_floor = float(review_policy.get("minimum_critical_score", 4.0))
    weighted_floor = float(review_policy.get("minimum_weighted_score", 84.0))
    maximum_score = int(review_policy.get("score_scale", {}).get("maximum", 5))
    minimum_score = int(review_policy.get("score_scale", {}).get("minimum", 1))

    ratings_by_id: dict[str, dict[str, Any]] = {}
    for index, rating in enumerate(ratings, start=1):
        context = f"critic_review.ratings[{index - 1}]"
        add_missing_key_errors(
            rating,
            package_policy.get("required_rating_keys", []),
            context,
            errors,
        )
        if not isinstance(rating, dict):
            continue
        rid = rating.get("direction_id")
        if not non_empty_string(rid):
            errors.append(f"{context}.direction_id must be a non-empty string.")
            continue
        if rid in ratings_by_id:
            errors.append(f"critic_review contains duplicate rating for direction {rid!r}.")
        ratings_by_id[rid] = rating

        scores = rating.get("dimension_scores")
        if not isinstance(scores, dict):
            errors.append(f"{context}.dimension_scores must be an object.")
            continue
        missing_dimensions = [dim for dim in required_dimensions if dim not in scores]
        extra_dimensions = [dim for dim in scores if dim not in required_dimensions]
        if missing_dimensions:
            errors.append(f"{context}.dimension_scores missing: {', '.join(missing_dimensions)}.")
        if extra_dimensions:
            errors.append(f"{context}.dimension_scores has unknown dimension(s): {', '.join(extra_dimensions)}.")

        valid_scores = True
        for dimension in required_dimensions:
            score = scores.get(dimension)
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not minimum_score <= score <= maximum_score:
                errors.append(
                    f"{context}.dimension_scores.{dimension} must be a number between {minimum_score} and {maximum_score}."
                )
                valid_scores = False

        computed_score: float | None = None
        if valid_scores and all(dim in scores for dim in required_dimensions):
            computed_score = round(
                sum((float(scores[dim]) / maximum_score) * float(weights[dim]) for dim in required_dimensions),
                1,
            )
            supplied_score = rating.get("weighted_score")
            if isinstance(supplied_score, bool) or not isinstance(supplied_score, (int, float)):
                errors.append(f"{context}.weighted_score must be numeric.")
            elif abs(float(supplied_score) - computed_score) > 0.2:
                errors.append(
                    f"{context}.weighted_score is {supplied_score}, but policy weights compute {computed_score}."
                )
            if rating.get("decision") == package_policy.get("passing_decision", "pass"):
                low_critical = [dim for dim in critical_dimensions if dim in scores and float(scores[dim]) < score_floor]
                if low_critical:
                    errors.append(
                        f"{context} cannot pass: critical dimension(s) below {score_floor}: {', '.join(low_critical)}."
                    )
                if computed_score < weighted_floor:
                    errors.append(
                        f"{context} cannot pass: weighted score {computed_score} is below {weighted_floor}."
                    )

        if not isinstance(rating.get("blockers"), list):
            errors.append(f"{context}.blockers must be an array.")
        elif rating.get("decision") == package_policy.get("passing_decision", "pass") and rating.get("blockers"):
            errors.append(f"{context} cannot pass while blockers remain.")

        if not isinstance(rating.get("revision_actions"), list):
            errors.append(f"{context}.revision_actions must be an array.")
        if rating.get("decision") not in ("pass", "revise", "reject"):
            errors.append(f"{context}.decision must be 'pass', 'revise', or 'reject'.")
        elif rating.get("decision") != package_policy.get("passing_decision", "pass"):
            errors.append(f"{context} is not passed by the independent critic (decision={rating.get('decision')!r}).")

    expected_direction_ids = set(direction_ids)
    if set(ratings_by_id) != expected_direction_ids:
        missing = sorted(expected_direction_ids - set(ratings_by_id))
        extra = sorted(set(ratings_by_id) - expected_direction_ids)
        if missing:
            errors.append(f"critic_review is missing scores for direction(s): {', '.join(missing)}.")
        if extra:
            errors.append(f"critic_review contains scores for unknown direction(s): {', '.join(extra)}.")

    if not non_empty_string(review.get("selection_rationale")):
        errors.append("critic_review.selection_rationale must be a non-empty string.")
    selected_id = review.get("selected_direction_id")
    if selected_id not in expected_direction_ids:
        errors.append("critic_review.selected_direction_id must match a direction ID.")
    elif selected_id in ratings_by_id and ratings_by_id[selected_id].get("decision") != "pass":
        errors.append("critic_review.selected_direction_id must identify a direction that passed critique.")

    # Generation configuration and candidate count.
    generation = package.get("generation_plan")
    if not isinstance(generation, dict):
        errors.append("generation_plan must be an object.")
        generation = {}
    for key in ("model", "backend", "requested_variants", "max_revision_cycles", "text_fidelity_policy"):
        if key not in generation:
            errors.append(f"generation_plan is missing required key {key!r}.")
    if generation.get("backend") != generation_policy.get("backend", "draw-things-cli"):
        errors.append(f"generation_plan.backend must be {generation_policy.get('backend', 'draw-things-cli')!r}.")
    expected_model = generation_policy.get("model_family", "qwen_image_2512")
    model = generation.get("model")
    if not non_empty_string(model) or expected_model.casefold() not in model.casefold():
        errors.append(f"generation_plan.model must identify the configured {expected_model} model family.")
    if isinstance(generation.get("requested_variants"), bool) or not isinstance(generation.get("requested_variants"), int):
        errors.append("generation_plan.requested_variants must be an integer.")
    elif generation.get("requested_variants") != len(directions):
        errors.append("generation_plan.requested_variants must equal the number of direction prompts.")
    max_cycles = generation.get("max_revision_cycles")
    configured_max = int(review_policy.get("maximum_revision_cycles", 2))
    if isinstance(max_cycles, bool) or not isinstance(max_cycles, int) or not 0 <= max_cycles <= configured_max:
        errors.append(f"generation_plan.max_revision_cycles must be an integer from 0 to {configured_max}.")
    if not non_empty_string(generation.get("text_fidelity_policy")):
        errors.append("generation_plan.text_fidelity_policy must explain exact-text verification and the typesetting fallback.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "mode": mode,
            "direction_count": len(directions),
            "reference_count": len(references),
            "critic_rating_count": len(ratings),
            "selected_direction_id": selected_id,
            "required_visible_text_fields": [label for _, label in required_visible_strings],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Cover Art System prompt package (structure and declared gates only)."
    )
    parser.add_argument("package", type=Path, help="Path to cover_prompt_package.json")
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY,
        help=f"Policy JSON path (default: {DEFAULT_POLICY})",
    )
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    args = parser.parse_args()

    try:
        package = load_json(args.package)
        policy = load_json(args.policy)
        result = validate_package(package, policy)
    except PackageValidationError as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)], "warnings": []}, indent=None if args.compact else 2))
        return 2

    print(json.dumps(result, indent=None if args.compact else 2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
