import json

from mar import log as explog
from mar.cli import main


def mar(capsys, tmp_path, *args):
    code = main(["--runs-dir", str(tmp_path / "runs"), "--experiments-dir", str(tmp_path / "exp"), *args])
    return code, capsys.readouterr().out


def files(tmp_path):
    b, a = tmp_path / "b.yaml", tmp_path / "a.yaml"
    b.write_text("value: 40\n")
    a.write_text("value: 30\n")
    return b, a


def test_record_appends_full_row(capsys, tmp_path):
    b, a = files(tmp_path)
    code, out = mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", "make it 30, not 40",
                    "--reason", "lower monthly cap", "--before", str(b), "--after", str(a), "--nwim")
    assert code == 0 and "not what I meant" in out
    r, = explog.read_rows(tmp_path / "exp" / "changes.jsonl")
    assert r["quote"] == "make it 30, not 40" and r["kind"] == "rule" and r["not_what_i_meant"] is True
    assert r["before_text"] == "value: 40\n" and r["after_text"] == "value: 30\n"
    assert "-value: 40" in r["diff"] and "+value: 30" in r["diff"]
    assert r["timestamp"].endswith("Z") and "git_commit" in r


def test_record_new_file_and_append_only(capsys, tmp_path):
    b, a = files(tmp_path)
    mar(capsys, tmp_path, "change", "record", "--kind", "oracle", "--quote", "q1", "--reason", "r", "--before", "-",
        "--after", str(a))
    first = (tmp_path / "exp" / "changes.jsonl").read_text()
    mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", "q2", "--reason", "r",
        "--before", str(b), "--after", str(a))
    text = (tmp_path / "exp" / "changes.jsonl").read_text()
    assert text.startswith(first) and len(text.splitlines()) == 2
    assert json.loads(first)["before_text"] == "" and json.loads(first)["not_what_i_meant"] is False


def test_list_and_bad_input(capsys, tmp_path):
    assert "No changes" in mar(capsys, tmp_path, "change", "list")[1]
    b, a = files(tmp_path)
    mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", "exact words", "--reason", "why",
        "--before", str(b), "--after", str(a))
    out = mar(capsys, tmp_path, "change", "list")[1]
    assert '"exact words"' in out and "-value: 40" in out
    assert mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", " ", "--reason", "x",
               "--before", "-", "--after", str(a))[0] == 2
    assert mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", "q", "--reason", "x",
               "--before", "-", "--after", "nofile.yaml")[0] == 2
