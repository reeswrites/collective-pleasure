from mar import frontier as F


def pts(d):
    return [{"variant": v, "freedom": f, "cooperation": c} for v, (f, c) in d.items()]


def test_pareto_drops_dominated():
    p = pts({"a": (0.9, 0.2), "b": (0.5, 0.8), "c": (0.4, 0.7), "d": (0.1, 0.9)})
    assert F.pareto(p) == ["d", "b", "a"]


def test_pareto_means_over_seeds_and_ties():
    p = pts({"a": (0.5, 0.5), "b": (0.5, 0.5)}) + [{"variant": "a", "freedom": 0.5, "cooperation": 0.5}]
    assert F.pareto(p) == ["a", "b"]  # equal points do not dominate each other


def test_chart_is_svg_in_both_themes():
    p = pts({"a": (0.9, 0.2), "b": (0.5, 0.8), "c": (0.4, 0.7)})
    for t in ("light", "dark"):
        s = F.frontier_chart(p, t)
        assert s.strip().startswith("<svg") and "<?xml" not in s and "b" in s
