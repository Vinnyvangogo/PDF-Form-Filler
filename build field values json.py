"""
build_field_values_json.py

Generates a ready-to-fill field_values.json for a PDF template, in the
exact format fill_atp_form.py (and the pdf skill's fill_fillable_fields.py)
expects:

    [
      {"field_id": "...", "page": 1, "value": ""},
      ...
    ]

Entries are ordered by page, then top-to-bottom, left-to-right (using each
field's rect), so the JSON reads in the same order fields appear on the
printed page -- easier to hand-edit or hand off to someone filling in
values.

- Text fields default to "" (empty string).
- Checkbox fields default to their unchecked_value (e.g. "/Off"), and get
  an extra "_checked_value" key noting what value would check them.

Usage:
    python3 build_field_values_json.py <field_info.json> <output_values.json>

field_info.json is produced by the pdf skill's
/mnt/skills/public/pdf/scripts/extract_form_field_info.py <template.pdf> <field_info.json>
"""
import json
import sys


def build(field_info_path, output_path):
    with open(field_info_path) as f:
        fields = json.load(f)

    # Sort by page, then top-to-bottom (higher y = higher on page, so
    # descending), then left-to-right.
    def sort_key(f):
        rect = f.get("rect", [0, 0, 0, 0])
        x0, y0 = rect[0], rect[1]
        return (f["page"], -y0, x0)

    fields_sorted = sorted(fields, key=sort_key)

    values = []
    for f in fields_sorted:
        entry = {"field_id": f["field_id"], "page": f["page"]}
        if f["type"] == "checkbox":
            entry["value"] = f.get("unchecked_value", "/Off")
            entry["_checked_value"] = f.get("checked_value", "/Yes")
        else:
            entry["value"] = ""
        values.append(entry)

    with open(output_path, "w") as f:
        json.dump(values, f, indent=2)

    print(f"Wrote {len(values)} field entries to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])
