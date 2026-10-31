# Schema additions (JSON Schema 2020-12)

Save each block under `.claude/schemas/` with the filename shown. They follow the repo conventions (`additionalProperties: false`, `schema_version` const `"1.0"`). Rule 18 requires every JSON output to validate against its schema before writing.

## `kit.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Digital Kit Manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "kit_id", "project_id", "positioning", "season", "audience_versions", "components", "skus", "variant_axes", "delivery"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "kit_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{2,79}$"},
    "project_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{2,79}$"},
    "positioning": {
      "type": "object", "additionalProperties": false,
      "required": ["promise", "buyer", "occasion"],
      "properties": {
        "promise": {"type": "string", "minLength": 10},
        "buyer": {"type": "string"},
        "occasion": {"type": "string"},
        "differentiators": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["claim", "evidence_ref"], "properties": {"claim": {"type": "string"}, "evidence_ref": {"type": "string"}}}},
        "competitor_gap": {"type": "string"}
      }
    },
    "season": {
      "type": "object", "additionalProperties": false,
      "required": ["occasion", "target_date", "latest_list_date"],
      "properties": {
        "occasion": {"type": "string"},
        "target_date": {"type": "string", "format": "date"},
        "latest_list_date": {"type": "string", "format": "date"},
        "evidence_refs": {"type": "array", "items": {"type": "string"}}
      }
    },
    "audience_versions": {
      "type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": false, "required": ["id", "band", "label"],
        "properties": {"id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"}, "band": {"type": "array", "minItems": 1, "items": {"enum": ["kids-4-8", "kids-6-10", "tween-8-12", "teen-13-17", "adult-general", "senior-large-print"]}}, "min_age": {"type": "integer", "minimum": 0}, "max_age": {"type": ["integer", "null"]}, "label": {"type": "string"}}}
    },
    "themes": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["id", "label"], "properties": {"id": {"type": "string"}, "label": {"type": "string"}}}},
    "components": {
      "type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": false, "required": ["id", "type", "count", "verifier"],
        "properties": {
          "id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
          "type": {"type": "string"},
          "count": {"type": "integer", "minimum": 1},
          "per_age_version": {"type": "boolean"},
          "per_theme": {"type": "boolean"},
          "authored_by": {"type": ["string", "null"]},
          "verifier": {"enum": ["code", "desk-check", "fact-check"]},
          "editable": {"type": "boolean"},
          "hazards": {"type": "array", "items": {"type": "string"}},
          "notes": {"type": "string"}
        }}
    },
    "skus": {
      "type": "array", "minItems": 1,
      "items": {"type": "object", "additionalProperties": false, "required": ["sku_id", "name", "includes", "licence_tier"],
        "properties": {
          "sku_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
          "name": {"type": "string"},
          "includes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
          "licence_tier": {"enum": ["personal", "classroom", "commercial"]},
          "price_recommendation": {"type": "object", "additionalProperties": false, "properties": {"amount": {"type": ["number", "null"]}, "currency": {"type": "string"}, "basis": {"type": "string"}}},
          "listing_overrides": {"type": "object"}
        }}
    },
    "variant_axes": {
      "type": "object", "additionalProperties": false,
      "required": ["page_size", "ink_mode", "age_version"],
      "properties": {
        "page_size": {"type": "array", "minItems": 1, "items": {"enum": ["us-letter", "a4"]}},
        "ink_mode": {"type": "array", "minItems": 1, "items": {"enum": ["full-colour", "ink-friendly"]}},
        "age_version": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "theme": {"type": "array", "items": {"type": "string"}}
      }
    },
    "delivery": {
      "type": "object", "additionalProperties": false,
      "required": ["strategy"],
      "properties": {
        "strategy": {"enum": ["zip-by-axis", "single-zip", "hosted-links"]},
        "split_axis": {"enum": ["age_version", "page_size", "ink_mode", "theme"]},
        "max_files": {"type": "integer", "minimum": 1},
        "max_file_mb": {"type": "number", "exclusiveMinimum": 0}
      }
    },
    "listing": {
      "type": "object", "additionalProperties": false,
      "properties": {
        "title_candidates": {"type": "array", "items": {"type": "string", "maxLength": 140}},
        "tag_candidates": {"type": "array", "items": {"type": "string", "maxLength": 20}},
        "category_candidate": {"type": "object", "additionalProperties": false, "properties": {"path": {"type": "string"}, "verified_on": {"type": ["string", "null"], "format": "date"}}},
        "image_plan_ref": {"type": "string"}
      }
    },
    "validation": {
      "type": "object", "additionalProperties": false,
      "properties": {"angle": {"type": "string"}, "hypothesis": {"type": "string"}, "test_plan_ref": {"type": "string"}}
    }
  }
}
```

## `craft-card.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Craft or Activity Card",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "card_id", "component_id", "age_version", "title", "difficulty", "min_age", "adult_supervision", "time_minutes", "materials", "steps", "hazard_tags", "make_tested"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "card_id": {"type": "string"},
    "component_id": {"type": "string"},
    "age_version": {"type": "string"},
    "title": {"type": "string", "maxLength": 60},
    "difficulty": {"enum": ["easy", "medium", "challenging"]},
    "min_age": {"type": "integer", "minimum": 3},
    "adult_supervision": {"enum": ["none", "nearby", "hands-on"]},
    "time_minutes": {"type": "integer", "minimum": 1, "maximum": 180},
    "materials": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": false, "required": ["id", "name", "quantity"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "quantity": {"type": "number", "exclusiveMinimum": 0}, "unit": {"type": "string"}, "optional": {"type": "boolean"}}}},
    "steps": {"type": "array", "minItems": 2, "items": {"type": "object", "additionalProperties": false, "required": ["n", "text", "uses_material_ids"], "properties": {"n": {"type": "integer", "minimum": 1}, "text": {"type": "string"}, "uses_material_ids": {"type": "array", "items": {"type": "string"}}, "adult_only": {"type": "boolean"}, "diagram_id": {"type": ["string", "null"]}}}},
    "hazard_tags": {"type": "array", "items": {"enum": ["scissors", "craft-knife", "hot-glue", "heat", "small-parts", "paint", "glitter", "sharp-point", "edible", "allergen", "water"]}},
    "precautions": {"type": "array", "items": {"type": "string"}},
    "make_tested": {"type": "boolean"},
    "make_test_evidence": {"type": ["object", "null"], "additionalProperties": false, "properties": {"tester": {"type": "string"}, "date": {"type": "string", "format": "date"}, "notes": {"type": "string"}}}
  }
}
```

## `fact-record.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Trivia / Fact Record",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "fact_id", "component_id", "question", "answer", "source_ids", "check"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "fact_id": {"type": "string"},
    "component_id": {"type": "string"},
    "question": {"type": "string"},
    "answer": {"type": "string"},
    "accepted_alternates": {"type": "array", "items": {"type": "string"}},
    "source_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "confidence": {"enum": ["high", "medium", "low"]},
    "check": {"type": "object", "additionalProperties": false, "required": ["status", "checked_by"], "properties": {"status": {"enum": ["confirmed", "disputed", "unverifiable", "pending"]}, "checked_by": {"type": "string"}, "checked_on": {"type": ["string", "null"], "format": "date"}, "note": {"type": "string"}}}
  }
}
```

## `etsy-listing-sku.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Etsy Listing Package (one SKU)",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "project_id", "sku_id", "title", "description", "tags", "category", "price", "licence_tier", "files", "images", "ai_disclosure", "external_write_performed"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "project_id": {"type": "string"},
    "sku_id": {"type": "string"},
    "title": {"type": "string", "maxLength": 140},
    "description": {"type": "string"},
    "tags": {"type": "array", "maxItems": 13, "uniqueItems": true, "items": {"type": "string", "minLength": 2, "maxLength": 20}},
    "category": {"type": "object", "additionalProperties": false, "required": ["path", "verified_on"], "properties": {"path": {"type": "string"}, "verified_on": {"type": ["string", "null"]}}},
    "price": {"type": "object", "additionalProperties": false, "required": ["amount", "currency", "status"], "properties": {"amount": {"type": ["number", "null"]}, "currency": {"type": "string"}, "status": {"const": "recommendation"}}},
    "licence_tier": {"enum": ["personal", "classroom", "commercial"]},
    "files": {"type": "array", "maxItems": 5, "items": {"type": "object", "additionalProperties": false, "required": ["name", "sha256", "size_mb"], "properties": {"name": {"type": "string"}, "sha256": {"type": "string"}, "size_mb": {"type": "number", "maximum": 20}}}},
    "images": {"type": "array", "maxItems": 10, "items": {"type": "object", "additionalProperties": false, "required": ["image_id", "role", "alt_text", "artifact_id"], "properties": {"image_id": {"type": "string"}, "role": {"type": "string"}, "alt_text": {"type": "string"}, "artifact_id": {"type": "string"}}}},
    "ai_disclosure": {"type": "string"},
    "limits_verified_on": {"type": ["string", "null"]},
    "external_write_performed": {"const": false}
  }
}
```

## `listing-image-plan.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Listing Image Plan",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "project_id", "sku_id", "images"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "project_id": {"type": "string"},
    "sku_id": {"type": "string"},
    "images": {
      "type": "array", "minItems": 1, "maxItems": 10,
      "items": {"type": "object", "additionalProperties": false, "required": ["image_id", "role", "size_px", "elements", "alt_text"],
        "properties": {
          "image_id": {"type": "string"},
          "role": {"enum": ["hero", "whats-included", "sample-pages", "versions-and-sizes", "how-it-works", "personalise", "licence-and-support", "faq-printing"]},
          "size_px": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "integer", "minimum": 1}},
          "headline_text": {"type": "string"},
          "elements": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["kind", "box"], "properties": {"kind": {"enum": ["page-raster", "text", "shape", "icon", "scene"]}, "source_artifact_id": {"type": ["string", "null"]}, "page": {"type": ["integer", "null"]}, "box": {"type": "array", "minItems": 4, "maxItems": 4, "items": {"type": "integer"}}, "text": {"type": "string"}, "transform": {"type": "object"}}}},
          "alt_text": {"type": "string"}
        }}
    }
  }
}
```
