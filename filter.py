import re

BRACKET_RE = re.compile(
    r"（[^（）]*）|\([^()]*\)|【[^【】]*】|\[[^\[\]]*\]|「[^「」]*」|『[^『』]*』"
)


def strip_brackets(text: str) -> str:
    if not any(c in text for c in "（）()【】[]「」『』"):
        return text.strip()
    for _ in range(10):
        prev = text
        text = BRACKET_RE.sub("", text)
        if text == prev:
            break
    text = text.strip()
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text
