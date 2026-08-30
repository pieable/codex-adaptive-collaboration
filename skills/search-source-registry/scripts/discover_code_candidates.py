#!/usr/bin/env python3
"""CLI for enumerating mature-code candidate projects across multiple ecosystems.

Only Python standard library APIs are used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


SUPPORTED_ECOSYSTEMS = ["github", "python", "npm", "rust", "go", "nuget"]
DEFAULT_LANG_BY_ECOSYSTEM = {
    "python": "Python",
    "rust": "Rust",
    "go": "Go",
    "nuget": "C#",
}
VALID_COVERAGE_STATUSES = {"ok", "partial", "error", "manual_required"}
GITHUB_QUERY_STOPWORDS = {
    "a",
    "an",
    "and",
    "csharp",
    "dotnet",
    "for",
    "go",
    "golang",
    "implementation",
    "java",
    "javascript",
    "libraries",
    "library",
    "mature",
    "node",
    "nodejs",
    "open",
    "opensource",
    "package",
    "packages",
    "project",
    "python",
    "rust",
    "source",
    "the",
    "tool",
    "tools",
    "typescript",
    "with",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--query",
        action="append",
        required=True,
        help="search query (can be repeated).",
    )
    parser.add_argument(
        "--ecosystem",
        action="append",
        choices=SUPPORTED_ECOSYSTEMS,
        default=None,
        help="ecosystem to query (can be repeated).",
    )
    parser.add_argument(
        "--language",
        help="optional language qualifier for GitHub searches.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="max results per source-query pair (1-50).",
    )
    parser.add_argument(
        "--enrich",
        type=int,
        default=5,
        help="number of candidates for per-record enrichment calls (0-10).",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=0,
        help="GitHub minimum stars filter.",
    )
    parser.add_argument(
        "--pushed-after",
        dest="pushed_after",
        help="GitHub pushed-at lower bound in YYYY-MM-DD.",
    )
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="include archived GitHub repositories.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout (seconds).",
    )
    parser.add_argument(
        "--output",
        help="write full JSON report to file; print only summary to stdout.",
    )
    parser.add_argument(
        "--user-agent",
        default="code-candidate-enumerator/1.0",
        help="User-Agent string used for outbound HTTP requests.",
    )

    args = parser.parse_args(argv)

    if args.max_results < 1 or args.max_results > 50:
        parser.error("--max-results must be in range 1..50")
    if args.enrich < 0 or args.enrich > 10:
        parser.error("--enrich must be in range 0..10")
    if args.min_stars < 0:
        parser.error("--min-stars must be >= 0")
    if args.timeout <= 0:
        parser.error("--timeout must be > 0")
    if args.pushed_after and not _is_valid_date(args.pushed_after):
        parser.error("--pushed-after must be YYYY-MM-DD")
    if args.language:
        args.language = args.language.strip()
        if not args.language:
            parser.error("--language must be non-empty if provided")
    if args.ecosystem is None:
        args.ecosystem = ["github"]
    else:
        deduped: List[str] = []
        for item in args.ecosystem:
            if item not in deduped:
                deduped.append(item)
        args.ecosystem = deduped
    return args


def _is_valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _coalesce(v: Optional[str]) -> str:
    return (v or "").strip()


def _get_json(url: str, headers: Dict[str, str], timeout: float) -> Tuple[Optional[int], Any, Dict[str, str], Optional[str]]:
    """Return (status_code, payload, headers, error)."""
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload: Any = None
            if text:
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    payload = text
            return response.status, payload, dict(response.headers), None
    except urllib.error.HTTPError as exc:
        body = None
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = None
        payload = None
        if body:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = body
        return exc.code, payload, dict(exc.headers), str(exc)
    except Exception as exc:  # includes URLError, timeout, network errors
        return None, None, {}, str(exc)


def _rate_limit_headers(headers: Dict[str, str]) -> Dict[str, str]:
    want = {
        "x-ratelimit-limit",
        "x-ratelimit-used",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "x-ratelimit-resource",
        "x-ratelimit-reset-time",
    }
    return {
        k: v
        for k, v in headers.items()
        if k.lower() in want
    }


def _normalize_repository_url(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None

    if text.startswith("git+"):
        text = text[4:]
    if text.startswith("git@github.com:"):
        text = "https://github.com/" + text[len("git@github.com:") :]
    if "@" in text and text.startswith("ssh://"):
        # e.g. ssh://git@github.com/owner/repo.git
        text = text.replace("ssh://git@", "https://")

    parsed = urllib.parse.urlparse(text)
    if parsed.scheme not in {"http", "https", "git", ""}:
        # handle raw scp-like github syntax not handled above
        pass
    if parsed.hostname is None:
        if text.startswith("github.com/"):
            path = text.split("github.com/", 1)[1]
            parsed_path = path
        else:
            return None
    else:
        if parsed.hostname.lower() not in {"github.com", "www.github.com"}:
            return None
        parsed_path = parsed.path
    parsed_path = parsed_path.split("#", 1)[0].split("?", 1)[0].strip("/")
    parts = [p for p in parsed_path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0].lower(), parts[1]
    repo = repo.lower()
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"https://github.com/{owner}/{repo}"


def _github_search_query(
    query: str,
    language: Optional[str],
    min_stars: int,
    pushed_after: Optional[str],
    include_archived: bool,
) -> str:
    parts = [query, "fork:false"]
    if not include_archived:
        parts.append("archived:false")
    if language:
        parts.append(f"language:{language}")
    if min_stars:
        parts.append(f"stars:>={min_stars}")
    if pushed_after:
        parts.append(f"pushed:>={pushed_after}")
    return " ".join(p for p in parts if p)


def _github_fallback_query(query: str, language: Optional[str]) -> Optional[str]:
    """Turn a sparse natural-language query into one bounded OR query."""
    if re.search(r"\bOR\b", query, flags=re.IGNORECASE):
        return None
    language_tokens = {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_.+#-]*", language or "")
    }
    tokens: List[str] = []
    seen = set()
    for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_.+#-]*", query):
        key = token.lower()
        if key in seen or key in language_tokens or key in GITHUB_QUERY_STOPWORDS:
            continue
        seen.add(key)
        tokens.append(token)
    if len(tokens) < 2:
        return None
    return " OR ".join(tokens[:4])


def _github_discover_items(
    query: str,
    language: Optional[str],
    per_page: int,
    min_stars: int,
    pushed_after: Optional[str],
    include_archived: bool,
    timeout: float,
    headers: Dict[str, str],
) -> Tuple[bool, List[Dict[str, Any]], Dict[str, Any], Optional[str], List[Dict[str, Any]]]:
    """Search GitHub and run at most one broader fallback when recall is sparse."""

    def search_once(raw_query: str, kind: str) -> Tuple[int, Any, Optional[str], Dict[str, Any]]:
        search = _github_search_query(
            raw_query, language, min_stars, pushed_after, include_archived
        )
        search_url = (
            "https://api.github.com/search/repositories"
            f"?q={urllib.parse.quote_plus(search)}&sort=stars&order=desc&per_page={per_page}"
        )
        status, payload, resp_headers, error = _get_json(search_url, headers, timeout)
        attempt: Dict[str, Any] = {
            "kind": kind,
            "query": raw_query,
            "search_query": search,
            "request_url": search_url,
            "http_status": status,
            "rate_limit": _rate_limit_headers(resp_headers),
        }
        if isinstance(payload, dict):
            attempt["total_count"] = payload.get("total_count")
            attempt["incomplete_results"] = payload.get("incomplete_results")
        if error:
            attempt["error"] = error
        return status, payload, error, attempt

    status, payload, error, primary_attempt = search_once(query, "primary")
    details: Dict[str, Any] = {
        "search_query": primary_attempt["search_query"],
        "request_url": primary_attempt["request_url"],
        "search_attempts": [primary_attempt],
    }
    partial_reasons: List[Dict[str, Any]] = []
    if status != 200 or not isinstance(payload, dict):
        return False, [], details, error or f"HTTP {status}", partial_reasons

    details["total_count"] = payload.get("total_count")
    details["incomplete_results"] = payload.get("incomplete_results")
    details["rate_limit"] = primary_attempt["rate_limit"]
    items = [item for item in (payload.get("items") or []) if isinstance(item, dict)]
    items = items[:per_page]

    fallback_query = _github_fallback_query(query, language)
    threshold = min(3, per_page)
    if len(items) < threshold and fallback_query:
        details["fallback_used"] = True
        details["fallback_reason"] = {
            "type": "sparse_primary_results",
            "primary_items": len(items),
            "threshold": threshold,
        }
        fb_status, fb_payload, fb_error, fallback_attempt = search_once(
            fallback_query, "broader_or_query"
        )
        details["search_attempts"].append(fallback_attempt)
        if fb_status == 200 and isinstance(fb_payload, dict):
            seen = {
                (_coalesce(item.get("full_name")).lower() or str(item.get("id")))
                for item in items
            }
            for item in fb_payload.get("items") or []:
                if not isinstance(item, dict):
                    continue
                key = _coalesce(item.get("full_name")).lower() or str(item.get("id"))
                if key in seen:
                    continue
                seen.add(key)
                items.append(item)
                if len(items) >= per_page:
                    break
        else:
            partial_reasons.append(
                {
                    "type": "github_fallback_lookup",
                    "query": fallback_query,
                    "status": fb_status,
                    "error": fb_error,
                }
            )
    else:
        details["fallback_used"] = False

    details["returned_after_merge"] = len(items)
    return True, items, details, None, partial_reasons


def _gh_headers(token: Optional[str], user_agent: str) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent,
        "X-GitHub-Api-Version": "2026-03-10",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _github_source_query(
    query: str,
    query_id: str,
    language: Optional[str],
    per_page: int,
    enrich: int,
    min_stars: int,
    pushed_after: Optional[str],
    include_archived: bool,
    timeout: float,
    headers: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    ok, items, search_details, error, search_partial_reasons = _github_discover_items(
        query,
        language,
        per_page,
        min_stars,
        pushed_after,
        include_archived,
        timeout,
        headers,
    )
    coverage = {
        "source": query_id,
        "query": query,
        "status": "ok",
        "details": search_details,
    }
    records: List[Dict[str, Any]] = []

    if not ok:
        coverage["status"] = "error"
        coverage["details"]["error"] = error
        return records, coverage
    if search_partial_reasons:
        coverage["status"] = "partial"
        coverage["details"].setdefault("partial_reasons", []).extend(
            search_partial_reasons
        )

    for index, item in enumerate(items[:per_page]):
        if not isinstance(item, dict):
            continue
        record = {
            "source": "github",
            "query_id": query_id,
            "query": query,
            "ecosystem": query_id,
            "name": item.get("name"),
            "full_name": item.get("full_name"),
            "description": item.get("description"),
            "repository_url": item.get("html_url"),
            "package_url": item.get("html_url"),
            "homepage": item.get("homepage"),
            "license_spdx_id": (item.get("license") or {}).get("spdx_id"),
            "language": item.get("language"),
            "topics": item.get("topics"),
            "stars": item.get("stargazers_count"),
            "forks": item.get("forks_count"),
            "open_issues": item.get("open_issues_count"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),
            "archived": item.get("archived"),
            "default_branch": item.get("default_branch"),
        }
        if index < enrich:
            full_name = _coalesce(item.get("full_name"))
            if full_name:
                release_url = f"https://api.github.com/repos/{urllib.parse.quote(full_name)}/releases/latest"
                rel_status, rel_payload, _, rel_error = _get_json(
                    release_url, headers, timeout
                )
                if rel_status == 200 and isinstance(rel_payload, dict):
                    record["github_release_latest"] = {
                        "tag_name": rel_payload.get("tag_name"),
                        "name": rel_payload.get("name"),
                        "published_at": rel_payload.get("published_at"),
                        "html_url": rel_payload.get("html_url"),
                        "draft": rel_payload.get("draft"),
                        "prerelease": rel_payload.get("prerelease"),
                    }
                elif rel_status == 404:
                    record["github_release_latest"] = None
                else:
                    record["github_release_latest_error"] = rel_error or f"HTTP {rel_status}"
                    coverage["status"] = "partial"
                    coverage["details"].setdefault("partial_reasons", []).append(
                        {
                            "type": "github_release_lookup",
                            "full_name": full_name,
                            "status": rel_status,
                        }
                    )

        records.append(record)

    return records, coverage


def _npm_source_query(
    query: str,
    per_page: int,
    timeout: float,
    user_agent: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    search_url = (
        "https://registry.npmjs.org/-/v1/search"
        f"?text={urllib.parse.quote_plus(query)}&size={per_page}"
    )
    headers = {"User-Agent": user_agent}
    status, payload, _, error = _get_json(search_url, headers, timeout)

    coverage = {
        "source": "npm",
        "query": query,
        "status": "ok",
        "details": {"request_url": search_url},
    }
    records: List[Dict[str, Any]] = []
    if status != 200 or not isinstance(payload, dict):
        coverage["status"] = "error"
        coverage["details"]["error"] = error or f"HTTP {status}"
        return records, coverage

    for obj in payload.get("objects", []):
        if not isinstance(obj, dict):
            continue
        package = obj.get("package") or {}
        score = obj.get("score") or {}
        detail = score.get("detail") or {}
        if not isinstance(package, dict):
            continue
        name = package.get("name")
        homepage = package.get("links", {}).get("homepage") if isinstance(package.get("links"), dict) else None
        homepage = homepage if isinstance(homepage, str) else None
        repo_url = package.get("links", {}).get("repository") if isinstance(package.get("links"), dict) else None
        package_url = package.get("links", {}).get("npm") if isinstance(package.get("links"), dict) else None
        records.append(
            {
                "source": "npm",
                "ecosystem": "npm",
                "query": query,
                "name": name,
                "description": package.get("description"),
                "repository_url": repo_url,
                "package_url": package_url,
                "version": package.get("version"),
                "homepage": homepage,
                "keywords": package.get("keywords"),
                "license": package.get("license"),
                "author": package.get("author"),
                "publisher": package.get("publisher"),
                "npm": obj.get("score") or {},
                "registry_signals": {
                    "downloads": obj.get("downloads"),
                    "dependents": obj.get("dependents"),
                    "registry_score_detail": detail,
                    "registry_score": score.get("final"),
                },
            }
        )
    return records[:per_page], coverage


def _crates_source_query(
    query: str,
    per_page: int,
    enrich: int,
    timeout: float,
    user_agent: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    search_params = urllib.parse.urlencode(
        {"q": query, "per_page": per_page, "page": 1}
    )
    search_url = f"https://crates.io/api/v1/crates?{search_params}"
    status, payload, _, error = _get_json(search_url, {"User-Agent": user_agent}, timeout)
    coverage = {"source": "rust", "query": query, "status": "ok", "details": {"request_url": search_url}}
    records: List[Dict[str, Any]] = []
    if status != 200 or not isinstance(payload, dict):
        coverage["status"] = "error"
        coverage["details"]["error"] = error or f"HTTP {status}"
        return records, coverage

    crates = payload.get("crates") or []
    if isinstance(crates, list):
        crates = [c for c in crates if isinstance(c, dict)]
    for index, item in enumerate(crates[:per_page]):
        if not isinstance(item, dict):
            continue
        name = item.get("id")
        record = {
            "source": "rust",
            "ecosystem": "rust",
            "query": query,
            "name": name,
            "description": item.get("description"),
            "repository_url": item.get("repository"),
            "package_url": f"https://crates.io/crates/{name}" if name else None,
            "crate_name": name,
            "max_version": item.get("max_version"),
            "newest_version": item.get("newest_version"),
            "downloads": item.get("downloads"),
            "recent_downloads": item.get("recent_downloads"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "categories": item.get("categories"),
            "keywords": item.get("keywords"),
            "homepage": item.get("homepage"),
            "documentation": item.get("documentation"),
        }
        if index < enrich and name:
            detail_url = f"https://crates.io/api/v1/crates/{urllib.parse.quote(name)}"
            d_status, d_payload, _, d_error = _get_json(
                detail_url, {"User-Agent": user_agent}, timeout
            )
            if d_status == 200 and isinstance(d_payload, dict):
                crate_info = d_payload.get("crate") or {}
                versions = d_payload.get("versions") or []
                latest = None
                max_ver = crate_info.get("max_stable_version") or crate_info.get("max_version")
                if isinstance(versions, list) and max_ver:
                    for v in versions:
                        if isinstance(v, dict) and v.get("num") == max_ver:
                            latest = v
                            break
                record["crates_io_latest"] = {
                    "license": latest.get("license") if isinstance(latest, dict) else None,
                    "rust_version": latest.get("rust_version") if isinstance(latest, dict) else None,
                    "max_stable_version": max_ver,
                    "latest_version": latest,
                }
            else:
                record["crates_io_latest_error"] = d_error or f"HTTP {d_status}"
                coverage["status"] = "partial"
                coverage["details"].setdefault("partial_reasons", []).append(
                    {"type": "crates_latest_lookup", "name": name, "status": d_status}
                )
        records.append(record)
    return records, coverage


def _go_source_query(
    query: str,
    per_page: int,
    timeout: float,
    user_agent: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    search_url = (
        "https://pkg.go.dev/v1beta/search?"
        + urllib.parse.urlencode({"q": query, "limit": per_page})
    )
    status, payload, _, error = _get_json(
        search_url, {"User-Agent": user_agent}, timeout
    )
    coverage = {"source": "go", "query": query, "status": "ok", "details": {"request_url": search_url}}
    records: List[Dict[str, Any]] = []
    if status != 200 or not isinstance(payload, dict):
        coverage["status"] = "error"
        coverage["details"]["error"] = error or f"HTTP {status}"
        return records, coverage

    for item in payload.get("items", [])[:per_page]:
        if not isinstance(item, dict):
            continue
        package_path = item.get("packagePath")
        module_path = item.get("modulePath")
        repo_url = _derive_github_repo_from_go_path(package_path, module_path)
        records.append(
            {
                "source": "go",
                "ecosystem": "go",
                "query": query,
                "name": item.get("name") or _coalesce(package_path).split("/")[-1],
                "description": item.get("synopsis"),
                "packagePath": package_path,
                "modulePath": module_path,
                "version": item.get("version"),
                "synopsis": item.get("synopsis"),
                "repository_url": repo_url,
                "package_url": (
                    f"https://pkg.go.dev/{package_path}" if package_path else None
                ),
                "registry_signals": {"search_score": item.get("score")},
            }
        )
    return records, coverage


def _derive_github_repo_from_go_path(package_path: Optional[str], module_path: Optional[str]) -> Optional[str]:
    candidates = [_coalesce(package_path), _coalesce(module_path)]
    for candidate in candidates:
        if candidate.startswith("github.com/"):
            parts = candidate.split("/")
            if len(parts) >= 3:
                owner, repo = parts[1], parts[2]
                if owner and repo:
                    return _normalize_repository_url(f"https://github.com/{owner}/{repo}")
    return None


def _nuget_index(timeout: float, user_agent: str) -> Tuple[Optional[str], Optional[str]]:
    headers = {"User-Agent": user_agent}
    status, payload, _, error = _get_json(
        "https://api.nuget.org/v3/index.json", headers, timeout
    )
    if status != 200 or not isinstance(payload, dict):
        return None, error or f"HTTP {status}"
    for resource in payload.get("resources", []) if isinstance(payload, dict) else []:
        if not isinstance(resource, dict):
            continue
        type_name = str(resource.get("@type") or "")
        if "SearchQueryService" in type_name:
            service_url = resource.get("@id")
            if isinstance(service_url, str):
                return service_url, None
    return None, "No SearchQueryService in NuGet index"


def _sanitize_nuget_search_url(base: str) -> str:
    # NuGet service templates sometimes include {?q,...}. Strip template part.
    return base.split("{", 1)[0]


def _nuget_source_query(
    query: str,
    per_page: int,
    timeout: float,
    user_agent: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    service_url, index_err = _nuget_index(timeout, user_agent)
    coverage = {"source": "nuget", "query": query, "status": "ok", "details": {}}
    records: List[Dict[str, Any]] = []
    if not service_url:
        coverage["status"] = "error"
        coverage["details"]["error"] = index_err
        return records, coverage

    base_url = _sanitize_nuget_search_url(service_url)
    params = urllib.parse.urlencode(
        {
            "q": query,
            "skip": 0,
            "take": per_page,
            "prerelease": "false",
            "semVerLevel": "2.0.0",
        }
    )
    search_url = f"{base_url}?{params}"
    status, payload, _, error = _get_json(
        search_url, {"User-Agent": user_agent}, timeout
    )
    coverage["details"]["request_url"] = search_url
    coverage["details"]["index_url"] = service_url
    if status != 200 or not isinstance(payload, dict):
        coverage["status"] = "error"
        coverage["details"]["error"] = error or f"HTTP {status}"
        return records, coverage

    for item in payload.get("data", []):
        if not isinstance(item, dict):
            continue
        project_url = item.get("projectUrl")
        versions = item.get("versions")
        if not isinstance(versions, list):
            versions = []
        records.append(
            {
                "source": "nuget",
                "ecosystem": "nuget",
                "query": query,
                "name": item.get("id"),
                "version": item.get("version"),
                "description": item.get("description"),
                "repository_url": _normalize_repository_url(project_url) if isinstance(project_url, str) else None,
                "package_url": f"https://www.nuget.org/packages/{item.get('id')}/",
                "authors": item.get("authors"),
                "totalDownloads": item.get("totalDownloads"),
                "verified": item.get("verified"),
                "tags": item.get("tags"),
                "projectUrl": project_url,
                "licenseUrl": item.get("licenseUrl"),
                "versions": versions,
            }
        )
    return records, coverage


def _python_source_query(
    query: str,
    query_id: str,
    per_page: int,
    enrich: int,
    min_stars: int,
    pushed_after: Optional[str],
    include_archived: bool,
    language: Optional[str],
    timeout: float,
    headers: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    # Use GitHub discovery, then optional exact-name PyPI enrichment.
    search_lang = language or "Python"
    ok, items, search_details, error, search_partial_reasons = _github_discover_items(
        query,
        search_lang,
        per_page,
        min_stars,
        pushed_after,
        include_archived,
        timeout,
        headers,
    )
    coverage = {
        "source": query_id,
        "query": query,
        "status": "ok",
        "details": search_details,
    }
    coverage["details"][
        "notes"
    ] = "PyPI enrichment is exact-name only; no full-text keyword search API for PyPI."
    if not ok:
        coverage["status"] = "error"
        coverage["details"]["error"] = error
        return [], coverage
    if search_partial_reasons:
        coverage["status"] = "partial"
        coverage["details"].setdefault("partial_reasons", []).extend(
            search_partial_reasons
        )

    records: List[Dict[str, Any]] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        name = _coalesce(item.get("name"))
        record = {
            "source": "python",
            "ecosystem": "python",
            "query": query,
            "query_id": query_id,
            "name": name,
            "full_name": item.get("full_name"),
            "description": item.get("description"),
            "repository_url": item.get("html_url"),
            "package_url": item.get("html_url"),
            "license_spdx_id": (item.get("license") or {}).get("spdx_id"),
            "language": item.get("language"),
            "topics": item.get("topics"),
            "stars": item.get("stargazers_count"),
            "forks": item.get("forks_count"),
            "open_issues": item.get("open_issues_count"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),
            "archived": item.get("archived"),
            "default_branch": item.get("default_branch"),
        }
        if idx < enrich and name:
            pypi_url = f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json"
            p_status, p_payload, _, p_error = _get_json(
                pypi_url, {"User-Agent": headers.get("User-Agent", "python")}, timeout
            )
            normalized_repo = _normalize_repository_url(record.get("repository_url"))
            matched = False
            if p_status == 200 and isinstance(p_payload, dict):
                info = p_payload.get("info") or {}
                project_urls = info.get("project_urls") or {}
                candidate_urls: List[str] = []
                if isinstance(project_urls, dict):
                    candidate_urls.extend(
                        [str(v) for v in project_urls.values() if isinstance(v, str)]
                    )
                project_url = info.get("project_url")
                if isinstance(project_url, str):
                    candidate_urls.append(project_url)
                home_page = info.get("home_page")
                if isinstance(home_page, str):
                    candidate_urls.append(home_page)
                for candidate in candidate_urls:
                    if _normalize_repository_url(candidate) == normalized_repo:
                        matched = True
                        break
                record["pypi_exact_match"] = matched
                if matched:
                    version = info.get("version")
                    release_files = (p_payload.get("releases") or {}).get(version, [])
                    upload_times = sorted(
                        str(file.get("upload_time_iso_8601"))
                        for file in release_files
                        if isinstance(file, dict) and file.get("upload_time_iso_8601")
                    )
                    record["pypi"] = {
                        "name": info.get("name"),
                        "version": version,
                        "summary": info.get("summary"),
                        "license": info.get("license_expression") or info.get("license"),
                        "requires_python": info.get("requires_python"),
                        "latest_upload_at": upload_times[-1] if upload_times else None,
                        "vulnerability_count": len(p_payload.get("vulnerabilities") or []),
                        "home_page": info.get("home_page"),
                        "project_urls": project_urls,
                    }
                else:
                    record["pypi_exact_match"] = False
                    coverage.setdefault("details", {}).setdefault(
                        "pypi_non_matches", []
                    ).append(name)
            elif p_status == 404:
                record["pypi_exact_match"] = False
                coverage.setdefault("details", {}).setdefault("pypi_not_found", []).append(name)
            else:
                record["pypi_error"] = p_error or f"HTTP {p_status}"
                coverage["status"] = "partial"
                coverage.setdefault("details", {}).setdefault("partial_reasons", []).append(
                    {"type": "pypi_lookup", "name": name, "status": p_status}
                )
        records.append(record)

    coverage["status"] = "partial"
    coverage.setdefault("details", {}).setdefault("manual_required_reasons", []).append(
        {
            "type": "pypi_full_text_discovery_unavailable",
            "reason": "PyPI supports exact-project metadata but no supported keyword search API.",
        }
    )
    if enrich > 0 and len(items) > enrich:
        coverage.setdefault("details", {}).setdefault("manual_required_reasons", []).append(
            {
                "type": "enrich_budget",
                "requested": enrich,
                "available": len(items),
                "query": query,
            }
        )
    elif enrich == 0 and records:
        coverage.setdefault("details", {}).setdefault("manual_required_reasons", []).append(
            {"type": "pypi_enrichment_not_performed", "requested": 0, "query": query}
        )

    if len(coverage.get("details", {}).get("pypi_not_found", [])) or len(
        coverage.get("details", {}).get("pypi_non_matches", [])
    ):
        coverage["status"] = "partial"

    return records, coverage


def _candidate_key(record: Dict[str, Any], source: str) -> Tuple[str, str, str]:
    repo = _normalize_repository_url(record.get("repository_url"))
    if repo:
        return ("repository", "repository", repo)
    package_url = _coalesce(record.get("package_url")).lower()
    if package_url:
        return ("package", source, package_url)
    name = _coalesce(record.get("name"))
    return ("identity", source, name)


def _add_record(
    candidate_index: Dict[Tuple[str, str, str], Dict[str, Any]],
    candidates: List[Dict[str, Any]],
    record: Dict[str, Any],
) -> None:
    source = record.get("source", "")
    key = _candidate_key(record, source)
    query = record.get("query")
    ecosystem = record.get("ecosystem", source)

    existing = candidate_index.get(key)
    if existing is None:
        # if we previously only had package-keyed item and now we discover repository, migrate
        if key[0] == "repository":
            alt_key = (
                "package",
                source,
                _coalesce(record.get("package_url")).lower(),
            )
            existing = candidate_index.get(alt_key)
            if existing is not None:
                del candidate_index[alt_key]
                existing["repository_url"] = _normalize_repository_url(
                    record.get("repository_url")
                )
                key = ("repository", "repository", existing["repository_url"])
                candidate_index[key] = existing

    if existing is None:
        existing = {
            "repository_url": _normalize_repository_url(record.get("repository_url")),
            "sources": [],
            "ecosystems": [],
            "matched_queries": [],
            "package_records": [],
        }
        candidate_index[key] = existing
        candidates.append(existing)

    for attr in ("sources",):
        if source and source not in existing[attr]:
            existing[attr].append(source)
    if ecosystem and ecosystem not in existing["ecosystems"]:
        existing["ecosystems"].append(ecosystem)
    match = {"source": source, "ecosystem": ecosystem, "query": query}
    if match not in existing["matched_queries"]:
        existing["matched_queries"].append(match)
    # keep raw records; explicit sources preserve all maturity signals
    existing["package_records"].append(record)


def _build_summary(
    candidates: List[Dict[str, Any]],
    coverage: List[Dict[str, Any]],
    request_meta: Dict[str, Any],
) -> Dict[str, Any]:
    status_counter = Counter(entry.get("status") for entry in coverage)
    by_source: Dict[str, Dict[str, int]] = defaultdict(lambda: Counter())
    for entry in coverage:
        source = str(entry.get("source", ""))
        by_source[source][str(entry.get("status"))] += 1
    return {
        "candidate_count": len(candidates),
        "coverage_entries": len(coverage),
        "source_queries_completed": sum(
            1 for entry in coverage if entry.get("status") in {"ok", "partial"}
        ),
        "request": request_meta,
        "by_status": dict(status_counter),
        "by_source": {k: dict(v) for k, v in by_source.items()},
    }


def _validate_coverage_status(status: str) -> None:
    if status not in VALID_COVERAGE_STATUSES:
        raise ValueError(f"invalid coverage status: {status}")


def run(args: argparse.Namespace) -> int:
    token = os.getenv("GITHUB_TOKEN")
    github_headers = _gh_headers(token, args.user_agent)

    coverage: List[Dict[str, Any]] = []
    candidate_index: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    candidates: List[Dict[str, Any]] = []

    for query in args.query:
        for ecosystem in args.ecosystem:
            q = _coalesce(query)
            if not q:
                continue
            effective_language = args.language
            if effective_language is None:
                effective_language = DEFAULT_LANG_BY_ECOSYSTEM.get(ecosystem)
            if ecosystem == "github":
                records, cov = _github_source_query(
                    q,
                    "github",
                    effective_language,
                    args.max_results,
                    args.enrich,
                    args.min_stars,
                    args.pushed_after,
                    args.include_archived,
                    args.timeout,
                    github_headers,
                )
            elif ecosystem == "python":
                records, cov = _python_source_query(
                    q,
                    "python",
                    args.max_results,
                    args.enrich,
                    args.min_stars,
                    args.pushed_after,
                    args.include_archived,
                    effective_language,
                    args.timeout,
                    github_headers,
                )
            elif ecosystem == "npm":
                records, cov = _npm_source_query(
                    q, args.max_results, args.timeout, args.user_agent
                )
            elif ecosystem == "rust":
                records, cov = _crates_source_query(
                    q,
                    args.max_results,
                    args.enrich,
                    args.timeout,
                    args.user_agent,
                )
            elif ecosystem == "go":
                records, cov = _go_source_query(
                    q, args.max_results, args.timeout, args.user_agent
                )
            elif ecosystem == "nuget":
                records, cov = _nuget_source_query(
                    q, args.max_results, args.timeout, args.user_agent
                )
            else:
                continue

            _validate_coverage_status(cov["status"])
            coverage.append(cov)
            for rec in records:
                _add_record(candidate_index, candidates, rec)

    request_meta = {
        "queries": args.query,
        "ecosystems": args.ecosystem,
        "max_results": args.max_results,
        "enrich": args.enrich,
        "min_stars": args.min_stars,
        "pushed_after": args.pushed_after,
        "include_archived": args.include_archived,
        "timeout": args.timeout,
        "user_agent": args.user_agent,
    }

    summary = _build_summary(candidates, coverage, request_meta)
    report = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "request": request_meta,
        "summary": summary,
        "coverage": coverage,
        "candidates": candidates,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(report, ensure_ascii=True, indent=2))

    if any(entry.get("status") in {"ok", "partial"} for entry in coverage):
        return 0
    return 2


def main() -> None:
    args = parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
