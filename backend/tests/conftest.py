"""
Pytest共通設定。

Ollama版では外部APIキーが不要になったため、
FastAPIのlifespanで必要になるのはChroma DBの一時パスのみ。
"""

import os
import tempfile

os.environ.setdefault("CHROMA_DB_DIR", os.path.join(tempfile.gettempdir(), "test_chroma_db"))
