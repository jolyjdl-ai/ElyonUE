from __future__ import annotations

import json
import math
import re
import threading
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = ROOT / "data" / "vector_index"
INDEX_FILE = INDEX_DIR / "index.json"
_LOCK = threading.Lock()

_TOK_REGEX = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9_]{2,}")

_IndexDoc = Dict[str, object]
_IndexState = Dict[str, object]

_state: _IndexState = {
    "doc_count": 0,
    "df": {},  # term -> document frequency
    "docs": {},  # doc_id -> {text, metadata, term_freq}
}


def _ensure_dir() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load() -> None:
    """Charge l'index depuis le disque si présent."""
    _ensure_dir()
    if INDEX_FILE.exists():
        try:
            data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _state["doc_count"] = int(data.get("doc_count", 0))
                _state["df"] = {str(k): int(v) for k, v in (data.get("df", {}) or {}).items()}
                docs = {}
                for doc_id, payload in (data.get("docs", {}) or {}).items():
                    if not isinstance(payload, dict):
                        continue
                    docs[str(doc_id)] = {
                        "text": str(payload.get("text", "")),
                        "metadata": payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {},
                        "term_freq": {
                            str(k): int(v) for k, v in (payload.get("term_freq", {}) or {}).items()
                        },
                        "length": int(payload.get("length", 0)),
                    }
                _state["docs"] = docs
        except Exception:
            # index corrompu -> on repart sur un état vide
            _state["doc_count"] = 0
            _state["df"] = {}
            _state["docs"] = {}
    else:
        _ensure_dir()


def save() -> None:
    """Persiste l'état courant sur le disque."""
    _ensure_dir()
    payload = {
        "doc_count": _state["doc_count"],
        "df": _state["df"],
        "docs": {},
    }
    for doc_id, meta in _state["docs"].items():
        payload["docs"][doc_id] = {
            "text": meta.get("text", ""),
            "metadata": meta.get("metadata", {}),
            "term_freq": meta.get("term_freq", {}),
            "length": meta.get("length", 0),
        }
    INDEX_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def reset() -> None:
    """Réinitialise complètement l'index (utilitaire dev/tests)."""
    with _LOCK:
        _state["doc_count"] = 0
        _state["df"] = {}
        _state["docs"] = {}
        save()


def _tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in _TOK_REGEX.finditer(text or "")]


def _update_df_for_terms(terms: Iterable[str], delta: int) -> None:
    df = _state["df"]
    for term in set(terms):
        current = df.get(term, 0) + delta
        if current <= 0:
            df.pop(term, None)
        else:
            df[term] = current


def _remove_doc_locked(doc_id: str) -> None:
    doc = _state["docs"].pop(doc_id, None)
    if not doc:
        return
    term_freq = doc.get("term_freq") or {}
    _update_df_for_terms(term_freq.keys(), -1)
    _state["doc_count"] = max(0, _state["doc_count"] - 1)


def ingest(text: str, doc_id: Optional[str] = None, metadata: Optional[Dict[str, object]] = None) -> str:
    """
    Ajoute ou remplace un document dans l'index et retourne son identifiant.
    """
    if not text:
        raise ValueError("Texte vide, impossible d'indexer")
    doc_id = doc_id or f"doc_{_state['doc_count'] + 1}"
    tokens = _tokenize(text)
    if not tokens:
        raise ValueError("Aucun token détecté après nettoyage")
    term_freq = Counter(tokens)
    with _LOCK:
        if doc_id in _state["docs"]:
            _remove_doc_locked(doc_id)
        _update_df_for_terms(term_freq.keys(), +1)
        _state["docs"][doc_id] = {
            "text": text,
            "metadata": metadata or {},
            "term_freq": dict(term_freq),
            "length": len(tokens),
        }
        _state["doc_count"] = len(_state["docs"])
        save()
    return doc_id


def ingest_file(path: Path, metadata: Optional[Dict[str, object]] = None) -> Optional[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    meta = metadata.copy() if isinstance(metadata, dict) else {}
    meta.setdefault("path", str(path))
    return ingest(text, doc_id=path.stem, metadata=meta)


def reindex_corpus(folder: Optional[Path] = None, extensions: Tuple[str, ...] = (".txt", ".md", ".json")) -> int:
    """Recharge un dossier complet (remplace l'index existant)."""
    folder = folder or (ROOT / "data" / "corpus")
    if not folder.exists():
        return 0
    paths = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
    with _LOCK:
        _state["doc_count"] = 0
        _state["df"] = {}
        _state["docs"] = {}
        save()
    count = 0
    for path in paths:
        doc_id = ingest_file(path, metadata={"source": "corpus"})
        if doc_id:
            count += 1
    return count


def _idf(term: str) -> float:
    df = _state["df"].get(term, 0)
    return math.log((1 + _state["doc_count"]) / (1 + df)) + 1.0


def _tfidf_vector(term_freq: Dict[str, int], doc_len: int) -> Tuple[Dict[str, float], float]:
    weights: Dict[str, float] = {}
    doc_len = max(1, doc_len)
    norm_sq = 0.0
    for term, count in term_freq.items():
        tf = count / doc_len
        idf = _idf(term)
        value = tf * idf
        weights[term] = value
        norm_sq += value * value
    return weights, math.sqrt(norm_sq) or 1.0


def _cosine_similarity(vec_a: Dict[str, float], norm_a: float, vec_b: Dict[str, float], norm_b: float) -> float:
    if not vec_a or not vec_b or norm_a == 0 or norm_b == 0:
        return 0.0
    score = 0.0
    for term, weight in vec_a.items():
        if term in vec_b:
            score += weight * vec_b[term]
    return score / (norm_a * norm_b)


def search(query: str, top_k: int = 3) -> List[Dict[str, object]]:
    tokens = _tokenize(query)
    if not tokens or _state["doc_count"] == 0:
        return []
    query_freq = Counter(tokens)
    query_vec, query_norm = _tfidf_vector(query_freq, len(tokens))
    results: List[Tuple[str, float]] = []
    for doc_id, doc_meta in _state["docs"].items():
        doc_vec, doc_norm = _tfidf_vector(doc_meta.get("term_freq", {}), doc_meta.get("length", 1))
        score = _cosine_similarity(query_vec, query_norm, doc_vec, doc_norm)
        if score > 0.0:
            results.append((doc_id, score))
    results.sort(key=lambda x: x[1], reverse=True)
    out = []
    for doc_id, score in results[: max(1, top_k)]:
        doc_meta = _state["docs"][doc_id]
        out.append(
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "text": doc_meta.get("text", ""),
                "metadata": doc_meta.get("metadata", {}),
            }
        )
    return out


# charger l'index à l'import
load()
