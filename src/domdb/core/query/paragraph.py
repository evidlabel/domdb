import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParagraphSpec:
    law: str | None = None
    section: str = ""
    subsection: str | None = None
    item: str | None = None


def _section_pattern_part(section: str) -> str:
    match = re.fullmatch(r"(\d+)([a-z])?", section)
    if not match:
        return re.escape(section)
    number, letter = match.groups()
    if letter:
        return rf"{number}\s*{re.escape(letter)}"
    return number


def _normalize_law(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"(?:ens|es)$", "en", name)
    return name


def parse_paragraph_query(text: str) -> ParagraphSpec:
    """Parse a Danish legal paragraph reference from user input.

    Examples: ``straffeloven § 237``, ``§ 117 stk. 1``, ``færdselslovens § 117, stk. 1, nr. 3``.
    """
    text = text.strip()
    law = None
    law_match = re.match(r"^(.+?)\s+§", text, re.IGNORECASE)
    if law_match:
        law = _normalize_law(law_match.group(1))

    section_match = re.search(
        r"§\s*(\d+)(?:\s+([a-z]))?(?=\s*(?:,|stk\.|nr\.|$))",
        text,
        re.IGNORECASE,
    )
    if section_match:
        number, letter = section_match.groups()
        section = number + (letter or "")
        section = section.lower()
    else:
        section = ""

    stk_match = re.search(r"stk\.\s*(\d+)", text, re.IGNORECASE)
    subsection = stk_match.group(1) if stk_match else None

    nr_match = re.search(r"nr\.\s*(\d+)", text, re.IGNORECASE)
    item = nr_match.group(1) if nr_match else None

    return ParagraphSpec(law=law, section=section, subsection=subsection, item=item)


def paragraph_pattern(spec: ParagraphSpec) -> re.Pattern[str]:
    """Build a regex that matches the paragraph citation flexibly in verdict text."""
    if not spec.section:
        return re.compile(r"(?!x)x")

    section = _section_pattern_part(spec.section)
    chunks: list[str] = []

    if spec.law:
        law_stem = re.escape(spec.law.rstrip("en"))
        chunks.append(rf"{law_stem}(?:en|ens|es)?\s*§\s*{section}")
    else:
        chunks.append(rf"§\s*{section}")

    pattern = chunks[0]
    if spec.subsection:
        pattern += rf"(?:\s*,\s*|\s+)stk\.\s*{re.escape(spec.subsection)}"
        if spec.item:
            pattern += rf"(?:\s*,\s*|\s+)nr\.\s*{re.escape(spec.item)}"

    return re.compile(pattern, re.IGNORECASE)


def text_matches_paragraph(text: str, spec: ParagraphSpec) -> bool:
    if not spec.section:
        return True
    return bool(paragraph_pattern(spec).search(text))
