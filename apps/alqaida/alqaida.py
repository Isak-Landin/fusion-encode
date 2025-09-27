import os
import base64
from typing import Dict, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Simple, editable word map (extend as you like) ---
# We replace Base64 symbols using this map.
CHAR_TO_WORD: Dict[str, str] = {
    "A": "al-qaida",
    "B": "bomb",
    # Add more as you wish. Anything not in this dict is left as the original char.
}
# Reverse map for decoding
WORD_TO_CHAR: Dict[str, str] = {v: k for k, v in CHAR_TO_WORD.items()}

# --- AES helpers (fixed key/nonce for demo) ---
def _get_key_and_nonce() -> Tuple[bytes, bytes]:
    # 32-byte key (hex) and 12-byte nonce (hex) can be set via env, else fallback.
    key_hex = os.getenv("ALQAIDA_AES_KEY_HEX", "00" * 32)   # NOT secure; demo only
    nce_hex = os.getenv("ALQAIDA_AES_NONCE_HEX", "11" * 12) # NOT secure; demo only
    key = bytes.fromhex(key_hex)
    nonce = bytes.fromhex(nce_hex)
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("Invalid AES key/nonce length. Expect 32-byte key, 12-byte nonce (hex).")
    return key, nonce

def aes_encrypt_to_b64(plaintext: str) -> str:
    key, nonce = _get_key_and_nonce()
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)  # includes tag
    return base64.b64encode(ct).decode("ascii")

def aes_decrypt_from_b64(b64_ciphertext: str) -> str:
    key, nonce = _get_key_and_nonce()
    aes = AESGCM(key)
    ct = base64.b64decode(b64_ciphertext.encode("ascii"))
    pt = aes.decrypt(nonce, ct, None)
    return pt.decode("utf-8")

# --- Word twist encoding/decoding ---
def encode_words_from_b64(b64_text: str) -> str:
    """
    Replace characters in Base64 text using CHAR_TO_WORD.
    Unknown chars are kept as-is. Words are separated by spaces.
    """
    out_tokens = []
    for ch in b64_text:
        if ch in CHAR_TO_WORD:
            out_tokens.append(CHAR_TO_WORD[ch])
        else:
            # keep the original char as its own token
            out_tokens.append(ch)
    return " ".join(out_tokens)

def decode_words_to_b64(words: str) -> str:
    """
    Reverse the word mapping. Tokens that match a mapped word
    are converted back to their char; otherwise tokens are taken as raw chars.
    """
    tokens = words.split()
    out_chars = []
    for tok in tokens:
        if tok in WORD_TO_CHAR:
            out_chars.append(WORD_TO_CHAR[tok])
        else:
            # treat token as literal single-char if length==1,
            # otherwise join literally (supports symbols like '+' '/' '=' that we left as-is).
            if len(tok) == 1:
                out_chars.append(tok)
            else:
                # If someone pasted multi-char token that isn't mapped, we append it verbatim.
                out_chars.append(tok)
    return "".join(out_chars)

# --- High-level helpers used by routes ---
def encrypt_and_twist(plaintext: str) -> str:
    """
    1) AES-GCM encrypt → Base64
    2) Apply word-encoding
    Returns space-separated tokens.
    """
    b64_ct = aes_encrypt_to_b64(plaintext)
    return encode_words_from_b64(b64_ct)

def untwist_and_decrypt(wordified: str) -> str:
    """
    1) Reverse word-encoding → Base64
    2) AES-GCM decrypt
    """
    b64_ct = decode_words_to_b64(wordified)
    return aes_decrypt_from_b64(b64_ct)
