"""Quick NMT smoke-test — run from the project root with the venv active.

Usage:
    python test_nmt.py

Checks:
  1. Which env vars are set (without printing secrets)
  2. Makes a single Azure Translator API call with a known-good string
  3. Prints the raw SDK response or the exact exception
"""

import os
import sys
from pathlib import Path

# ── 1. Load .env ──────────────────────────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file, override=False)
    print(f"[env] Loaded {env_file}")
else:
    print(f"[env] No .env file found at {env_file}")

# ── 2. Check credentials ──────────────────────────────────────────────────────
endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "")
key      = os.environ.get("AZURE_TRANSLATOR_KEY", "")
region   = os.environ.get("AZURE_TRANSLATOR_REGION", "")
target   = os.environ.get("AZURE_TRANSLATOR_TARGET_LANGUAGE", "en")

print()
print("[config]")
print(f"  AZURE_TRANSLATOR_ENDPOINT = {repr(endpoint) if not endpoint else repr(endpoint[:30] + '...')}")
print(f"  AZURE_TRANSLATOR_KEY      = {'<set, {} chars>'.format(len(key)) if key else '<NOT SET>'}")
print(f"  AZURE_TRANSLATOR_REGION   = {repr(region) if region else '<not set>'}")
print(f"  AZURE_TRANSLATOR_TARGET_LANGUAGE = {repr(target)}")

if not endpoint or not key:
    print()
    print("[ERROR] Missing AZURE_TRANSLATOR_ENDPOINT or AZURE_TRANSLATOR_KEY.")
    print("        Set them in .env (copy .env.example) and re-run.")
    sys.exit(1)

# ── 3. Try the SDK call ───────────────────────────────────────────────────────
TEST_TEXT = "王强又名王小强"
print()
print(f"[test] Translating: {repr(TEST_TEXT)} → '{target}'")

try:
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    client = TextTranslationClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        region=region if region else None,
    )
    response = client.translate(
        body=[{"text": TEST_TEXT}],
        to_language=[target],
        from_language="zh",
    )
    print("[response] raw:", response)
    if response and response[0].translations:
        print("[result] translated:", response[0].translations[0].text)
    else:
        print("[result] empty response — no translation returned")

except ImportError as e:
    print(f"[ERROR] SDK not installed: {e}")
    print("        Run: pip install azure-ai-translation-text")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
