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
