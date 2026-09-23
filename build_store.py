"""Build pam's static ONLYOFFICE marketplace from pinned official sources."""
import argparse
import concurrent.futures
import hashlib
import io
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "upstream-manifest.json").read_text())
AI_SHA256 = "5e98cc51659cdf3fd0edcdf076137893575f4840a5fa6dcb2f460f93c8669c43"
AI_ARCHIVE = "sdkjs-plugins/content/ai/deploy/ai.plugin"


def build(cache=None):
    revision = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    output = ROOT / "_site"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()

    def fetch(item):
        path, expected = item
        cached = cache / path if cache else None
        if cached and cached.is_file():
            data = cached.read_bytes()
        else:
            url = f"https://raw.githubusercontent.com/ONLYOFFICE/onlyoffice.github.io/{MANIFEST['commit']}/{path}"
            request = urllib.request.Request(url, headers={"User-Agent": "pam-onlyoffice-build"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected:
            raise ValueError(f"Upstream content mismatch: {path}")
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, MANIFEST["files"].items()))

    archive = (output / AI_ARCHIVE).read_bytes()
    if hashlib.sha256(archive).hexdigest() != AI_SHA256:
        raise ValueError("The official AI package checksum does not match")
    plugin_root = output / "sdkjs-plugins/content/ai"
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        for entry in package.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Invalid archive path: {entry.filename}")
        package.extractall(plugin_root)

    # The official plugin's relative SDK references require this second location.
    shutil.copytree(output / "sdkjs-plugins/v1", output / "sdkjs-plugins/content/v1")
    (output / "store/config.json").write_text('[\n  {"name": "ai", "offered": "Ascensio System SIA"}\n]\n')

    for html in (output / "store").rglob("*.html"):
        sdk_path = Path(os.path.relpath(output / "sdkjs-plugins/v1", html.parent)).as_posix()
        source = html.read_text()
        source = source.replace("https://onlyoffice.github.io/sdkjs-plugins/v1", sdk_path)
        if html.parent == output / "store":
            source = source.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<title>pam · Marketplace ONLYOFFICE</title>\n<meta name="robots" content="noindex,nofollow">\n<link rel="icon" href="../favicon.svg">', 1)
        if html.name == "index.html" and html.parent == output / "store":
            source = source.replace("<aside>", '<aside>\n<div style="padding:16px 20px 12px;font-size:20px;font-weight:600">pam</div>', 1)
            source = source.replace("</aside>", '<div style="padding:12px 20px;font-size:12px"><a class="link" href="PAM-SOURCE.md" target="_blank" rel="noreferrer">Source &amp; licences</a></div>\n</aside>', 1)
        html.write_text(source)

    replacements = {
        "store/scripts/code.js": (
            "plugin.baseUrl ? releaseUrl + pluginFileName + '.plugin' : ''",
            "plugin.baseUrl ? plugin.baseUrl + 'deploy/' + pluginFileName + '.plugin' : ''",
        ),
        "store/scripts/shared/data-fetcher.js": (
            "_urlToCheckConnection: 'https://onlyoffice.github.io/store/translations/langs.json'",
            "_urlToCheckConnection: new URL('translations/langs.json', window.location.href).href",
        ),
    }
    for relative, (old, new) in replacements.items():
        target = output / relative
        source = target.read_text()
        if source.count(old) != 1:
            raise ValueError(f"Unexpected upstream source: {relative}")
        target.write_text(source.replace(old, new, 1))

    # Keep the explicitly selected AI release visible. The upstream store hides
    # this GUID after AI was integrated into newer editors, including in browsers.
    code = output / "store/scripts/code.js"
    source = code.read_text()
    store_patches = [
        ("MarketplaceStorage.excludeAiPluginIfNeeded();", "// pam: retain the AI release explicitly selected in this catalogue."),
        ("config.url = confUrl;", "config.offered = config.offered || plugin.offered;\n\t\t\t\t\tconfig.url = confUrl;"),
        ("DataFetcher.makeRequest(configUrl, 'GET', null, null)", f"DataFetcher.makeRequest(configUrl + '?v={revision}', 'GET', null, null)"),
    ]
    for old, new in store_patches:
        if source.count(old) != 1:
            raise ValueError(f"Unexpected marketplace source: {old}")
        source = source.replace(old, new, 1)
    code.write_text(source)

    shutil.copyfile(ROOT / "favicon.svg", output / "favicon.svg")
    shutil.copyfile(ROOT / "PAM-SOURCE.md", output / "store/PAM-SOURCE.md")
    (output / "index.html").write_text('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>pam · ONLYOFFICE</title><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url=store/index.html"></head><body><a href="store/index.html">Ouvrir le catalogue pam</a></body></html>\n')
    (output / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (output / ".nojekyll").touch()

    # GitHub Pages caches static URLs for ten minutes. Content hashes prevent a
    # newly loaded HTML page from mixing old scripts with the new catalogue.
    for html in (output / "store").rglob("*.html"):
        def version_asset(match):
            attr, relative = match.groups()
            asset = html.parent / relative
            if asset.suffix not in (".js", ".css") or not asset.is_file():
                return match.group(0)
            digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
            return f'{attr}="{relative}?v={digest}"'
        html.write_text(re.sub(r'(src|href)="([^"?:]+)"', version_asset, html.read_text()))
    config = json.loads((plugin_root / "config.json").read_text())
    print(f"Built pam with AI {config['version']}; SHA-256 {AI_SHA256}")
    print(f"Static files: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, help="Optional directory containing verified upstream files")
    build(parser.parse_args().cache)
