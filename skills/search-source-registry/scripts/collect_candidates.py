#!/usr/bin/env python3
"""Enumerate semiconductor-news candidates from registered official entry points."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zoneinfo import ZoneInfo


SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = SKILL_DIR / "references" / "sources.json"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}"
DEFAULT_USER_AGENT = "Codex semiconductor news research contact@example.invalid"
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0 Safari/537.36"
)

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3,
    "march": 3, "apr": 4, "april": 4, "may": 5, "jun": 6,
    "june": 6, "jul": 7, "july": 7, "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("时间必须包含时区，例如 2026-08-01T00:00:00+08:00")
    return parsed


def fetch(url: str, user_agent: str, timeout: float) -> bytes:
    effective_user_agent = user_agent if re.search(r"(?:^|\.)sec\.gov/", url) else BROWSER_USER_AGENT
    request = Request(
        url,
        headers={
            "User-Agent": effective_user_agent,
            "Accept": "application/json, application/atom+xml, application/rss+xml, text/html;q=0.9, */*;q=0.5",
            "Accept-Encoding": "identity",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_json(url: str, user_agent: str, timeout: float) -> Any:
    return json.loads(fetch(url, user_agent, timeout).decode("utf-8"))


def decode_page(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "big5", "shift_jis", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def us_dst(day: date) -> bool:
    march_first = date(day.year, 3, 1)
    second_sunday_march = 8 + (6 - march_first.weekday()) % 7
    november_first = date(day.year, 11, 1)
    first_sunday_november = 1 + (6 - november_first.weekday()) % 7
    return date(day.year, 3, second_sunday_march) <= day < date(day.year, 11, first_sunday_november)


def named_zone(name: str, day: date | None = None) -> timezone | ZoneInfo:
    try:
        return ZoneInfo(name)
    except Exception:
        reference_day = day or datetime.now(timezone.utc).date()
        fixed_offsets = {
            "UTC": 0,
            "Asia/Taipei": 8,
            "Asia/Tokyo": 9,
            "Asia/Shanghai": 8,
        }
        if name == "America/New_York":
            hours = -4 if us_dst(reference_day) else -5
        elif name == "America/Los_Angeles":
            hours = -7 if us_dst(reference_day) else -8
        elif name in fixed_offsets:
            hours = fixed_offsets[name]
        else:
            raise RuntimeError(f"缺少时区数据库且没有 {name} 的内置后备偏移")
        return timezone(timedelta(hours=hours), name)


def source_zone(source: dict[str, Any]) -> timezone | ZoneInfo:
    return named_zone(source.get("timezone", "UTC"))


def calendar_date_in_window(day: date, zone: timezone | ZoneInfo, since: datetime, until: datetime) -> bool:
    first = since.astimezone(zone).date()
    last = (until.astimezone(zone) - timedelta(microseconds=1)).date()
    return first <= day <= last


def parse_date_hint(text_value: str, zone: timezone | ZoneInfo) -> tuple[datetime | date | None, str]:
    normalized = re.sub(r"\s+", " ", html.unescape(text_value))

    iso_datetime = re.search(r"\b(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)\b", normalized)
    if iso_datetime:
        try:
            parsed = datetime.fromisoformat(iso_datetime.group(1).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=zone)
            return parsed, "datetime"
        except ValueError:
            pass

    numeric = re.search(r"\b(20\d{2})[./-](0?[1-9]|1[0-2])[./-](0?[1-9]|[12]\d|3[01])\b", normalized)
    if numeric:
        try:
            return date(int(numeric.group(1)), int(numeric.group(2)), int(numeric.group(3))), "date"
        except ValueError:
            pass

    month_first = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+([0-3]?\d)(?:st|nd|rd|th)?[,]?\s+(20\d{2})\b",
        normalized,
        flags=re.I,
    )
    if month_first:
        try:
            return date(int(month_first.group(3)), MONTHS[month_first.group(1).lower()], int(month_first.group(2))), "date"
        except (KeyError, ValueError):
            pass

    day_first = re.search(
        r"\b([0-3]?\d)\s+(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?[,]?\s+(20\d{2})\b",
        normalized,
        flags=re.I,
    )
    if day_first:
        try:
            return date(int(day_first.group(3)), MONTHS[day_first.group(2).lower()], int(day_first.group(1))), "date"
        except (KeyError, ValueError):
            pass

    return None, "unknown"


def date_matches(value: datetime | date, precision: str, zone: timezone | ZoneInfo, since: datetime, until: datetime) -> bool:
    if precision == "datetime":
        assert isinstance(value, datetime)
        return since <= value.astimezone(since.tzinfo) < until
    assert isinstance(value, date)
    return calendar_date_in_window(value, zone, since, until)


def date_to_text(value: datetime | date | None, precision: str) -> str | None:
    if value is None:
        return None
    if precision == "datetime":
        assert isinstance(value, datetime)
        return value.isoformat()
    return value.isoformat()


def candidate_id(source_id: str, url: str, published_at: str | None) -> str:
    raw = f"{source_id}\n{url}\n{published_at or ''}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def make_candidate(
    source: dict[str, Any], title: str, url: str, published: datetime | date | None,
    precision: str, **extra: Any,
) -> dict[str, Any]:
    published_text = date_to_text(published, precision)
    item = {
        "id": candidate_id(source["id"], url, published_text),
        "source_id": source["id"],
        "source_name": source["name"],
        "company": extra.pop("company", source.get("company")),
        "region": source.get("region"),
        "category": source.get("category"),
        "title": clean_text(title),
        "url": url,
        "published_at": published_text,
        "date_precision": precision,
    }
    item.update({key: value for key, value in extra.items() if value not in (None, "")})
    return item


def collect_html(
    source: dict[str, Any], since: datetime, until: datetime, user_agent: str,
    timeout: float, include_undated: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw = fetch(source["url"], user_agent, timeout)
    page = decode_page(raw)
    zone = source_zone(source)
    allow = re.compile(source.get("allow", "."), flags=re.I)
    deny = re.compile(source.get("deny", r"privacy|cookie|terms|contact|career|facebook|linkedin|twitter"), flags=re.I)
    anchor_pattern = re.compile(
        r"<a\b[^>]*?href\s*=\s*([\"'])(.*?)\1[^>]*>(.*?)</a>", flags=re.I | re.S
    )
    candidates: list[dict[str, Any]] = []
    scanned = 0
    seen: set[str] = set()
    generic = {"read more", "more", "learn more", "details", "view all", "next", "previous"}

    for match in anchor_pattern.finditer(page):
        href = html.unescape(match.group(2)).strip()
        title = clean_text(match.group(3))
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        url = urljoin(source["url"], href)
        if deny.search(url) or not allow.search(f"{url} {title}"):
            continue
        if len(title) < 8 or title.lower() in generic:
            continue
        scanned += 1
        context = clean_text(page[max(0, match.start() - 700): min(len(page), match.end() + 700)])
        published, precision = parse_date_hint(context, zone)
        if published is None:
            if not include_undated:
                continue
            precision = "unknown"
        elif not date_matches(published, precision, zone, since, until):
            continue
        normalized = url.split("#", 1)[0]
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(make_candidate(source, title, normalized, published, precision))

    coverage = {
        "source_id": source["id"], "source_name": source["name"], "status": "ok",
        "url": source["url"], "scanned": scanned, "emitted": len(candidates),
    }
    return candidates, coverage


def xml_text(element: ElementTree.Element, names: tuple[str, ...]) -> str:
    for child in element.iter():
        local = child.tag.rsplit("}", 1)[-1].lower()
        if local in names and child.text:
            return child.text.strip()
    return ""


def collect_rss(
    source: dict[str, Any], since: datetime, until: datetime, user_agent: str, timeout: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = ElementTree.fromstring(fetch(source["url"], user_agent, timeout))
    zone = source_zone(source)
    entries = [item for item in root.iter() if item.tag.rsplit("}", 1)[-1].lower() in ("item", "entry")]
    candidates: list[dict[str, Any]] = []
    for entry in entries:
        title = xml_text(entry, ("title",))
        link = xml_text(entry, ("link",))
        if not link:
            for child in entry.iter():
                if child.tag.rsplit("}", 1)[-1].lower() == "link" and child.attrib.get("href"):
                    link = child.attrib["href"]
                    break
        raw_date = xml_text(entry, ("pubdate", "published", "updated", "date"))
        published: datetime | date | None = None
        precision = "unknown"
        if raw_date:
            try:
                published = parsedate_to_datetime(raw_date)
                if published.tzinfo is None:
                    published = published.replace(tzinfo=zone)
                precision = "datetime"
            except (TypeError, ValueError, OverflowError):
                published, precision = parse_date_hint(raw_date, zone)
        if not title or not link or published is None:
            continue
        if date_matches(published, precision, zone, since, until):
            candidates.append(make_candidate(source, title, urljoin(source["url"], link), published, precision))
    return candidates, {
        "source_id": source["id"], "source_name": source["name"], "status": "ok",
        "url": source["url"], "scanned": len(entries), "emitted": len(candidates),
    }


def sec_ticker_map(user_agent: str, timeout: float) -> dict[str, dict[str, Any]]:
    payload = fetch_json(SEC_TICKERS_URL, user_agent, timeout)
    return {row["ticker"].upper(): row for row in payload.values()}


def collect_one_sec_company(
    ticker: str, ticker_map: dict[str, dict[str, Any]], source: dict[str, Any],
    since: datetime, until: datetime, user_agent: str, timeout: float,
) -> tuple[list[dict[str, Any]], int, str | None]:
    mapping = ticker_map.get(ticker.upper())
    if not mapping:
        return [], 0, f"ticker_not_found:{ticker}"
    cik = int(mapping["cik_str"])
    payload = fetch_json(SEC_SUBMISSIONS_URL.format(cik=cik), user_agent, timeout)
    recent = payload.get("filings", {}).get("recent", {})
    allowed_forms = set(source.get("forms", []))
    rows = zip(
        recent.get("accessionNumber", []), recent.get("filingDate", []),
        recent.get("reportDate", []), recent.get("acceptanceDateTime", []),
        recent.get("act", []), recent.get("form", []), recent.get("fileNumber", []),
        recent.get("filmNumber", []), recent.get("items", []), recent.get("size", []),
        recent.get("isXBRL", []), recent.get("isInlineXBRL", []),
        recent.get("primaryDocument", []), recent.get("primaryDocDescription", []),
    )
    candidates: list[dict[str, Any]] = []
    scanned = 0
    for row in rows:
        (
            accession, filing_date, report_date, accepted, _act, form, _file_number,
            _film_number, items, _size, _is_xbrl, _inline_xbrl, document, description,
        ) = row
        if form not in allowed_forms:
            continue
        scanned += 1
        try:
            published = datetime.fromisoformat(accepted.replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = published.replace(tzinfo=named_zone("America/New_York", published.date()))
            precision = "datetime"
        except (AttributeError, ValueError):
            published = date.fromisoformat(filing_date)
            precision = "date"
        if not date_matches(published, precision, named_zone("America/New_York", published.date()), since, until):
            continue
        url = SEC_ARCHIVE_URL.format(cik=cik, accession=accession.replace("-", ""), document=document)
        title = f"{mapping['title']} {form}"
        if description:
            title += f": {description}"
        candidates.append(make_candidate(
            source, title, url, published, precision, company=mapping["title"], ticker=ticker.upper(),
            form=form, accession_number=accession, report_date=report_date or None,
            filing_date=filing_date or None, items=items or None,
        ))
    return candidates, scanned, None


def collect_sec(
    source: dict[str, Any], since: datetime, until: datetime, user_agent: str,
    timeout: float, workers: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ticker_map = sec_ticker_map(user_agent, timeout)
    candidates: list[dict[str, Any]] = []
    scanned = 0
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as executor:
        futures = {
            executor.submit(
                collect_one_sec_company, ticker, ticker_map, source, since, until, user_agent, timeout
            ): ticker
            for ticker in source.get("tickers", [])
        }
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                found, count, error = future.result()
                candidates.extend(found)
                scanned += count
                if error:
                    errors.append(error)
            except Exception as exc:  # source-level output must retain partial failures
                errors.append(f"{ticker}:{type(exc).__name__}:{exc}")
    status = "ok" if not errors else ("partial" if candidates or scanned else "error")
    coverage: dict[str, Any] = {
        "source_id": source["id"], "source_name": source["name"], "status": status,
        "url": SEC_TICKERS_URL, "scanned": scanned, "emitted": len(candidates),
        "companies_requested": len(source.get("tickers", [])),
    }
    if errors:
        coverage["errors"] = errors
    return candidates, coverage


def dedupe(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for item in candidates:
        key = item["url"].split("#", 1)[0].rstrip("/").lower()
        unique.setdefault(key, item)
    return sorted(unique.values(), key=lambda item: (item.get("published_at") or "", item["source_id"], item["title"]), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", required=True, type=parse_iso)
    parser.add_argument("--until", required=True, type=parse_iso)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source", action="append", dest="source_ids")
    parser.add_argument("--include-undated", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT", DEFAULT_USER_AGENT))
    args = parser.parse_args()
    if args.since >= args.until:
        parser.error("--since 必须早于 --until")

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    selected = set(args.source_ids or [])
    sources = [source for source in registry["sources"] if not selected or source["id"] in selected]
    if selected:
        missing = sorted(selected - {source["id"] for source in sources})
        if missing:
            parser.error(f"未知来源: {', '.join(missing)}")

    candidates: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    source_checks_completed = 0
    for source in sources:
        kind = source["kind"]
        if kind == "manual":
            coverage.append({
                "source_id": source["id"], "source_name": source["name"],
                "status": "manual_required", "url": source.get("url"), "reason": source.get("reason"),
            })
            continue
        try:
            if kind == "sec_submissions":
                found, source_coverage = collect_sec(
                    source, args.since, args.until, args.user_agent, args.timeout, args.workers
                )
            elif kind == "html_links":
                found, source_coverage = collect_html(
                    source, args.since, args.until, args.user_agent, args.timeout, args.include_undated
                )
            elif kind == "rss":
                found, source_coverage = collect_rss(source, args.since, args.until, args.user_agent, args.timeout)
            else:
                raise ValueError(f"unsupported source kind: {kind}")
            candidates.extend(found)
            coverage.append(source_coverage)
            if source_coverage["status"] in ("ok", "partial"):
                source_checks_completed += 1
        except Exception as exc:
            coverage.append({
                "source_id": source["id"], "source_name": source["name"], "status": "error",
                "url": source.get("url"), "error": f"{type(exc).__name__}: {exc}",
            })

    candidates = dedupe(candidates)
    counts: dict[str, int] = {}
    for row in coverage:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    result = {
        "registry_version": registry.get("version"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": {"since": args.since.isoformat(), "until": args.until.isoformat(), "semantics": "[since, until)"},
        "summary": {
            "sources_selected": len(sources), "coverage_by_status": counts,
            "source_checks_completed": source_checks_completed, "candidate_count": len(candidates),
            "warning": "候选尚未核验；manual_required 和 error 不算已覆盖。",
        },
        "coverage": coverage,
        "candidates": candidates,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), **result["summary"]}, ensure_ascii=False))
    else:
        print(rendered)
    return 0 if source_checks_completed else 2


if __name__ == "__main__":
    sys.exit(main())
