"""
fill_atp_form.py

Fills the CPS 8281 / CPS 8282 ATP PDF templates using their REAL AcroForm
fields (not a text overlay -- these templates have actual fillable fields,
640 in CPS 8281 and 833 in CPS 8282).

Field values are supplied as a JSON list in this format (same convention as
extract_form_field_info.py / fill_fillable_fields.py in the pdf skill):

    [
      {"field_id": "Serial Number of MCU1", "page": 1, "value": "SN-00123"},
      {"field_id": "Pass",                  "page": 1, "value": "X"},
      ...
    ]

- field_id must match a real field name in the template (see
  list_pdf_fields.py / extract_form_field_info.py to get valid names).
- page must match the field's actual page (1-based) -- this catches
  typos/duplicate-name mismatches early.
- For checkboxes, use the field's checked/unchecked value (see
  extract_form_field_info.py output, "checked_value"/"unchecked_value").

Usage:
    python3 fill_atp_form.py <input.pdf> <field_values.json> <output.pdf>
"""
import json
import sys
from pypdf import PdfReader, PdfWriter


def load_field_info(reader):
    """Build field_id -> {page, type, checked_value, unchecked_value} map
    directly from the PDF (mirrors extract_form_field_info.py's output)."""
    info = {}
    fields = reader.get_fields() or {}

    for page_num, page in enumerate(reader.pages, start=1):
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            name = _full_name(annot)
            if not name or name in info:
                continue
            field = fields.get(name, {})
            ftype_code = field.get("/FT")
            entry = {"page": page_num}
            if ftype_code == "/Btn":
                states = field.get("/_States_", [])
                on_states = [s for s in states if s != "/Off"]
                entry["type"] = "checkbox"
                entry["checked_value"] = on_states[0] if on_states else "/Yes"
                entry["unchecked_value"] = "/Off"
            else:
                entry["type"] = "text"
            info[name] = entry
    return info


def _full_name(annot):
    parts = []
    node = annot
    seen = set()
    while node is not None:
        t = node.get("/T")
        if t:
            parts.append(str(t))
        parent = node.get("/Parent")
        if parent is None or id(parent) in seen:
            break
        seen.add(id(parent))
        node = parent.get_object() if hasattr(parent, "get_object") else parent
    return ".".join(reversed(parts))


def fill_pdf(input_pdf_path, field_values_json_path, output_pdf_path):
    with open(field_values_json_path) as f:
        field_values = json.load(f)

    reader = PdfReader(input_pdf_path)
    field_info = load_field_info(reader)

    # Validate + group by page
    values_by_page = {}
    had_error = False
    for entry in field_values:
        field_id = entry["field_id"]
        page = entry["page"]
        value = entry["value"]

        info = field_info.get(field_id)
        if info is None:
            print(f"ERROR: '{field_id}' is not a valid field name in this PDF")
            had_error = True
            continue
        if info["page"] != page:
            print(f"ERROR: '{field_id}' is on page {info['page']}, not {page}")
            had_error = True
            continue
        if info["type"] == "checkbox":
            valid = {info["checked_value"], info["unchecked_value"]}
            if value not in valid:
                print(f"ERROR: '{field_id}' is a checkbox; value must be one "
                      f"of {valid}, got '{value}'")
                had_error = True
                continue

        values_by_page.setdefault(page, {})[field_id] = value

    if had_error:
        print("Aborting: fix the errors above before filling.")
        sys.exit(1)

    writer = PdfWriter(clone_from=reader)
    for page, values in values_by_page.items():
        writer.update_page_form_field_values(
            writer.pages[page - 1], values, auto_regenerate=False
        )
    writer.set_need_appearances_writer(True)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"Filled {sum(len(v) for v in values_by_page.values())} fields "
          f"across {len(values_by_page)} page(s) -> {output_pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    fill_pdf(sys.argv[1], sys.argv[2], sys.argv[3])
