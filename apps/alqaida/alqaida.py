# apps/alqaida/alqaida.py
import os
import json
import base64
import binascii
from typing import Dict, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---- Base64 alphabet we must cover ----
BASE64_ALPHABET = (
    [chr(c) for c in range(ord('A'), ord('Z') + 1)] +
    [chr(c) for c in range(ord('a'), ord('z') + 1)] +
    [str(d) for d in range(10)] +
    ['+', '/', '=']  # padding
)

# ---- Built-in minimal defaults (only A/B populated per your earlier example) ----
# If wordlist.json is missing/invalid, we’ll use CHAR_TO_WORD_BUILTIN and warn.
CHAR_TO_WORD_BUILTIN: Dict[str, str] = {
    "A": "al-qaida",
    "B": "bomb",
    # everything else falls back to literal characters (encoded as single-token)
}
# Reverse built-in
WORD_TO_CHAR_BUILTIN: Dict[str, str] = {v: k for k, v in CHAR_TO_WORD_BUILTIN.items()}

# ---- Load/validate external wordlist ----
def _load_wordlist(path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Load JSON mapping of Base64 characters -> single-token words.
    Ensures: (1) all 65 Base64 symbols are present,
             (2) values are unique strings without spaces,
             (3) every key is a single symbol from the alphabet.
    Returns (char_to_word, word_to_char).
    Raises ValueError on validation errors.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("wordlist must be a JSON object {char: word, ...}")

    # Check keys
    keys = set(data.keys())
    required = set(BASE64_ALPHABET)
    missing = required - keys
    extra = keys - required
    if missing:
        raise ValueError(f"wordlist missing keys: {sorted(missing)}")
    if extra:
        raise ValueError(f"wordlist has unsupported keys: {sorted(extra)}")

    # Check values
    values = list(data.values())
    if any(not isinstance(v, str) or v.strip() == "" for v in values):
        raise ValueError("wordlist values must be non-empty strings")
    if any(" " in v for v in values):
        raise ValueError("wordlist values must not contain spaces (space is the token separator)")
    if len(set(values)) != len(values):
        raise ValueError("wordlist values must be unique")

    # Build reverse map
    inv = {}
    for k, v in data.items():
        if v in inv:
            raise ValueError(f"duplicate value: {v}")
        inv[v] = k

    return data, inv

def _init_mapping() -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Try to load mapping from config/wordlist.json (or ALQAIDA_WORDLIST_PATH env).
    If anything fails, fall back to built-in minimal defaults (A/B only).
    Unmapped chars will pass through as literal single-char tokens.
    """
    path = os.getenv("ALQAIDA_WORDLIST_PATH", "config/wordlist.json")
    try:
        if os.path.exists(path):
            ctow, wtoc = _load_wordlist(path)
            return ctow, wtoc
    except Exception as e:
        # Print once so you can see why it fell back (container logs)
        print(f"[alqaida] wordlist load failed: {e} — falling back to built-in mapping")

    return CHAR_TO_WORD_BUILTIN, WORD_TO_CHAR_BUILTIN

CHAR_TO_WORD, WORD_TO_CHAR = _init_mapping()

# ---- AES (fixed key/nonce for reproducible demo) ----
def _get_key_and_nonce() -> Tuple[bytes, bytes]:
    # 32-byte key (hex) and 12-byte nonce (hex)
    key_hex = os.getenv("ALQAIDA_AES_KEY_HEX", "00" * 32)    # NOT secure; demo only
    nce_hex = os.getenv("ALQAIDA_AES_NONCE_HEX", "11" * 12)  # NOT secure; demo only
    try:
        key = bytes.fromhex(key_hex)
        nonce = bytes.fromhex(nce_hex)
    except binascii.Error as e:
        raise ValueError(f"Bad hex in ALQAIDA_AES_KEY_HEX/ALQAIDA_AES_NONCE_HEX: {e}")
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("Invalid AES key/nonce length. Expect 32-byte key and 12-byte nonce (hex).")
    return key, nonce

def aes_encrypt_to_b64(plaintext: str) -> str:
    key, nonce = _get_key_and_nonce()
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)  # includes GCM tag
    return base64.b64encode(ct).decode("ascii")

def aes_decrypt_from_b64(b64_ciphertext: str) -> str:
    key, nonce = _get_key_and_nonce()
    aes = AESGCM(key)
    ct = base64.b64decode(b64_ciphertext.encode("ascii"))
    pt = aes.decrypt(nonce, ct, None)
    return pt.decode("utf-8")

# ---- Word “twist” encoding/decoding ----
def encode_words_from_b64(b64_text: str) -> str:
    """
    For each Base64 character, emit its mapped word if present; otherwise the
    literal character as a single token. Tokens are space-separated.
    """
    out_tokens = []
    for ch in b64_text:
        word = CHAR_TO_WORD.get(ch)
        out_tokens.append(word if word is not None else ch)
    return " ".join(out_tokens)

def decode_words_to_b64(words: str) -> str:
    """
    Reverse: space-split tokens; if token is a mapped word, convert to the
    original Base64 char; else if token length==1, treat as literal char.
    """
    tokens = words.split()
    out_chars = []
    for tok in tokens:
        if tok in WORD_TO_CHAR:
            out_chars.append(WORD_TO_CHAR[tok])
        elif len(tok) == 1:
            out_chars.append(tok)
        else:
            # Unrecognized multi-char token — treat literally so the user sees the error on decrypt.
            out_chars.append(tok)
    return "".join(out_chars)

# ---- High-level used by routes ----
def encrypt_and_twist(plaintext: str) -> str:
    b64_ct = aes_encrypt_to_b64(plaintext)
    return encode_words_from_b64(b64_ct)

def untwist_and_decrypt(wordified: str) -> str:
    b64_ct = decode_words_to_b64(wordified)
    return aes_decrypt_from_b64(b64_ct)
