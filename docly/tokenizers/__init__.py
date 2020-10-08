from tokenize import tokenize
from io import BytesIO


def tokenize_code_string(text):
    code_tokens = []
    for tok in tokenize(BytesIO(text.encode('utf-8')).readline):
        if tok.string.strip() != "" and tok.string.strip() != "utf-8":
            code_tokens.append(tok.string.strip().lower())
    return code_tokens