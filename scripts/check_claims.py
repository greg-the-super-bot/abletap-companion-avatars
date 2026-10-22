#!/usr/bin/env python3
"""Layer-1 claims checker (copied from imparted-web/scripts/check_claims.py, 2026-10-18;
keep the two in step). Here it checks abletap.io: site/ against scripts/ABLETAP-CLAIMS.md
and the shared register in the brain vault (_brain/CLAIMS-REGISTER.md).

Web HTML/JavaScript is scanned as rendered-source text. Swift is scanned only
inside ordinary ("...") and multiline (\"\"\"...\"\"\") string literals so
identifiers and comments do not create false positives.

Usage: check_claims.py <source_root> [register_path]   (exit 1 on violations)
"""
import re, sys, glob, os, html

WEB_GLOBS = ("**/*.html", "**/*.js", "**/*.txt")   # .txt: llms.txt tells AI assistants what to say
SWIFT_GLOB = "**/*.swift"

def load_register(path):
    txt = open(path, encoding="utf-8").read()
    y = re.search(r"```yaml(.*?)```", txt, re.S).group(1)
    def grab(key):
        block = re.search(key + r":\n((?:  - .*\n)+)", y)
        if not block:
            return []
        out = []
        for l in block.group(1).strip().split("\n"):
            v = l.strip()[2:].strip()
            if v[:1] in ("'", '"'):
                v = v[1:-1]
            out.append(v)
        return out
    prices = re.search(r"allowed_prices: \[(.*?)\]", y).group(1)
    prices = [p.strip().strip('"').strip("'") for p in prices.split(",")]
    return prices, grab("banned_patterns"), grab("allowed_contexts")

def overlapping_allowed_context(text, match, allowed):
    for phrase in allowed:
        for allowed_match in re.finditer(re.escape(phrase), text):
            if allowed_match.start() < match.end() and allowed_match.end() > match.start():
                return True
    return False

def check_text(text, relpath, first_line, prices, banned, allowed, violations):
    low = html.unescape(text).lower()
    for offset, line in enumerate(low.split("\n")):
        line_number = first_line + offset
        for pat in banned:
            for match in re.finditer(pat, line):
                if overlapping_allowed_context(line, match, allowed):
                    continue
                context = line[max(0, match.start()-60):match.end()+60]
                violations.append(
                    "%s:%d: banned /%s/ -> ...%s..."
                    % (relpath, line_number, pat, context.strip()[:100])
                )
        for match in re.finditer(r"\$(\d{1,3}(?:\.\d{2})?)\b", line):
            value = match.group(1)
            if "." in value and value not in prices:
                context = line[max(0, match.start()-50):match.end()+50]
                violations.append(
                    "%s:%d: off-register price $%s -> ...%s..."
                    % (relpath, line_number, value, context.strip()[:90])
                )

def swift_string_literals(text):
    """Yield (body, first_line) for non-raw Swift string literals.

    A small lexer is preferable to a whole-file regex here because quoted text
    inside // and /* */ comments is not a Swift string and must not fail builds.
    """
    index = 0
    length = len(text)
    while index < length:
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            index = length if newline == -1 else newline + 1
            continue
        if text.startswith("/*", index):
            depth = 1
            index += 2
            while index < length and depth:
                if text.startswith("/*", index):
                    depth += 1
                    index += 2
                elif text.startswith("*/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            continue
        if text.startswith('"""', index):
            body_start = index + 3
            closing = text.find('"""', body_start)
            body_end = length if closing == -1 else closing
            yield text[body_start:body_end], text.count("\n", 0, body_start) + 1
            index = length if closing == -1 else closing + 3
            continue
        if text[index] == '"':
            body_start = index + 1
            index = body_start
            escaped = False
            while index < length:
                character = text[index]
                if character == "\n":
                    break
                if character == '"' and not escaped:
                    break
                if character == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False
                index += 1
            yield text[body_start:index], text.count("\n", 0, body_start) + 1
            if index < length and text[index] == '"':
                index += 1
            continue
        index += 1

def check_swift(text, relpath, prices, banned, allowed, violations):
    for body, first_line in swift_string_literals(text):
        # allowed_contexts describe truthful web-only exceptions such as
        # printable resources and the current web offer. They must not suppress
        # a banned iOS claim merely because the words are valid on the web.
        check_text(body, relpath, first_line, prices, banned, [], violations)

def main():
    root = sys.argv[1]
    reg = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "CLAIMS-REGISTER.md")
    prices, banned, allowed = load_register(reg)
    violations = []
    web_files = [
        f
        for pattern in WEB_GLOBS
        for f in glob.glob(os.path.join(root, pattern), recursive=True)
    ]
    swift_files = glob.glob(os.path.join(root, SWIFT_GLOB), recursive=True)
    files = sorted(set(web_files + swift_files))
    for f in sorted(set(files)):
        text = open(f, encoding="utf-8", errors="replace").read()
        relpath = os.path.relpath(f, root)
        if f.endswith(".swift"):
            check_swift(text, relpath, prices, banned, allowed, violations)
        else:
            check_text(text, relpath, 1, prices, banned, allowed, violations)
    if violations:
        print("CLAIMS CHECK FAILED - %d violation(s):" % len(violations))
        for v in violations:
            print("  " + v)
        sys.exit(1)
    print("CLAIMS CHECK OK - %d files scanned, 0 violations" % len(files))

if __name__ == "__main__":
    main()
