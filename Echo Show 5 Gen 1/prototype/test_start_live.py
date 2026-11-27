"""Offline checks with synthetic values; never opens the user's .env."""
import pathlib
import runpy
import tempfile
from unittest import mock

x = runpy.run_path(str(pathlib.Path(__file__).with_name("start-live")))
keys = x["KEYS"]
values = dict(zip(keys, ["synthetic-client", "https://example.invalid", "a" * 40]))
content = "\n".join(k + "=" + v for k, v in values.items())
assert x["parse"](content) == values
assert x["parse"]("# comment\n\n" + content) == values
for bad in [content + "\n" + keys[0] + "=duplicate", content + "\nUNKNOWN=secret",
            content.replace("https:", "http:"), content.replace("a" * 40, "x"),
            content.replace("synthetic-client", ""), content.replace("example.invalid", "user:pass@example.invalid")]:
    try:
        x["parse"](bad)
    except ValueError:
        pass
    else:
        raise AssertionError("bad config accepted")
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / ".env"
    p.write_text(content)
    p.chmod(0o600)
    assert x["load"](p) == values
    p.chmod(0o644)
    try:
        x["load"](p)
    except ValueError:
        pass
    else:
        raise AssertionError("insecure permissions accepted")
    p.chmod(0o600)
    link = p.with_name("link")
    link.symlink_to(p)
    try:
        x["load"](link)
    except OSError:
        pass
    else:
        raise AssertionError("symlink accepted")
    p.unlink()
    with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("sys.stderr.isatty", return_value=True), mock.patch("getpass.getpass", side_effect=list(values.values())):
        assert x["setup"](p) == values
    assert p.stat().st_mode & 0o777 == 0o600
    assert x["load"](p) == values
print("Launcher: 14 synthetic assertions passed")
