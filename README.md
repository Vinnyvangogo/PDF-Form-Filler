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
    
------------------------------------------------------------------------------------------

list_pdf_fields.py

Reads all AcroForm field names from a PDF template and writes them to a
plain text file (one field name per line, plus type/page metadata).

Usage:
    python3 list_pdf_fields.py <input.pdf> <output.txt>

Example:
    python3 list_pdf_fields.py CPS_8281_Rev_A_ATP_Template.pdf CPS_8281_field_names.txt

-----------------------------------------------------------------------------------------

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
    
