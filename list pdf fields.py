"""
list_pdf_fields.py

Reads all AcroForm field names from a PDF template and writes them to a
plain text file (one field name per line, plus type/page metadata).

Usage:
    python3 list_pdf_fields.py <input.pdf> <output.txt>

Example:
    python3 list_pdf_fields.py CPS_8281_Rev_A_ATP_Template.pdf CPS_8281_field_names.txt
"""
import sys
from pypdf import PdfReader

FIELD_TYPE_NAMES = {
    "/Tx": "text",
    "/Btn": "button/checkbox/radio",
    "/Ch": "choice",
    "/Sig": "signature",
}


def get_full_field_name(field):
    """Walk up /Parent chain to build the fully-qualified field name
    (matches how Acrobat displays nested field names, e.g. 'Parent.Child')."""
    parts = []
    node = field
    seen = set()
    while node is not None:
        t = node.get("/T")
        if t:
            parts.append(str(t))
        parent = node.get("/Parent")
        if parent is None or id(parent) in seen:
            break
        seen.add(id(parent))
        node = parent
    return ".".join(reversed(parts))


def list_fields(pdf_path, output_path):
    reader = PdfReader(pdf_path)

    # page -> list of field names on that page (via annotations)
    page_of_field = {}
    for page_num, page in enumerate(reader.pages, start=1):
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") == "/Widget":
                name = get_full_field_name(annot)
                if name:
                    page_of_field.setdefault(name, page_num)

    fields = reader.get_fields() or {}

    lines = []
    lines.append(f"Field names for: {pdf_path}")
    lines.append(f"Total fields found: {len(fields)}")
    lines.append("=" * 60)

    for name in sorted(fields.keys()):
        info = fields[name]
        ftype_code = info.get("/FT")
        ftype = FIELD_TYPE_NAMES.get(ftype_code, str(ftype_code))
        page = page_of_field.get(name, "?")
        default_value = info.get("/DV", "")
        line = f"{name}\t[type={ftype}]\t[page={page}]"
        if default_value not in ("", None):
            line += f"\t[default={default_value}]"
        lines.append(line)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(fields)} field names to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    list_fields(sys.argv[1], sys.argv[2])
