#!/usr/bin/env python3
"""Tests for the scoring and the linter. Synthetic numbers only.

  python3 ads/engine/test_ads.py
"""
import copy
import sys
import unittest
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ads  # noqa: E402


def tot(rows):
    t = defaultdict(lambda: defaultdict(float))
    for ad_id, m in rows.items():
        t[ad_id].update(m)
    return t


def video(imp, views, q25, clicks, spend, meetings=0):
    return {"impressions": imp, "video_views": views, "video_q25": q25, "clicks": clicks, "spend": spend, "meetings": meetings}


VIDEO = {"concept": "k", "angle": "speed", "persona": "demand-gen", "awareness": "problem", "format": "video-creator", "hook": "pov", "campaign": "t"}


class Score(unittest.TestCase):
    def test_hook_trap_is_not_a_winner(self):
        # Wispr's example: 39.5% 3-second hook rate, only 14.3% made it to 25%.
        data = {"T-001": video(20000, 7900, 1130, 60, 900),
                "T-002": video(20000, 4000, 1800, 90, 900),
                "T-003": video(20000, 3600, 1700, 80, 900),
                "T-004": video(20000, 3000, 1300, 70, 900)}
        ads_ = {k: VIDEO for k in data}
        rows = {r["ad_id"]: r for r in ads.score(tot(data), ads_)}
        self.assertTrue(rows["T-001"]["hook_trap"])
        self.assertNotEqual(rows["T-001"]["verdict"], "winner")
        self.assertAlmostEqual(rows["T-001"]["raw_hook"], 0.395)
        self.assertAlmostEqual(rows["T-001"]["raw_hold"], 1130 / 7900)
        self.assertGreater(rows["T-002"]["banger"], rows["T-001"]["banger"])

    def test_small_samples_are_still_learning(self):
        data = {"T-001": video(400, 200, 150, 40, 20), "T-002": video(20000, 4000, 1800, 90, 900)}
        rows = {r["ad_id"]: r for r in ads.score(tot(data), {k: VIDEO for k in data})}
        self.assertEqual(rows["T-001"]["verdict"], "learning")
        # 10% raw CTR on 400 impressions is shrunk toward the cohort, not taken at face value
        self.assertLess(rows["T-001"]["ctr"], 0.05)

    def test_server_side_meetings_outweigh_clicks(self):
        img = dict(VIDEO, format="img-1x1")
        data = {"T-001": {"impressions": 30000, "clicks": 300, "spend": 1500, "meetings": 0},
                "T-002": {"impressions": 30000, "clicks": 150, "spend": 1500, "meetings": 6},
                "T-003": {"impressions": 30000, "clicks": 200, "spend": 1500, "meetings": 2}}
        rows = {r["ad_id"]: r for r in ads.score(tot(data), {k: img for k in data})}
        self.assertGreater(rows["T-002"]["banger"], rows["T-001"]["banger"])
        self.assertEqual(rows["T-002"]["conv_metric"], "meetings")


class Lint(unittest.TestCase):
    def setUp(self):
        self.camp = copy.deepcopy(ads.load("pageview-to-pipeline"))

    def errors(self):
        return ads.lint_campaign("pageview-to-pipeline", self.camp, quiet=True)[0]

    def test_example_is_clean(self):
        self.assertEqual(self.errors(), [])

    def test_invented_number(self):
        self.camp["ads"][0]["copy"]["intro"] = "Teams book 3x more meetings."
        self.assertTrue(any("no source" in e for e in self.errors()))

    def test_sourced_number(self):
        self.camp["ads"][0]["copy"]["intro"] = "And 55+ other tools."
        self.assertEqual(self.errors(), [])

    def test_competitor(self):
        self.camp["ads"][0]["copy"]["headline"] = "Better than Drift."
        self.assertTrue(any("competitor" in e for e in self.errors()))

    def test_unknown_tag(self):
        self.camp["ads"][0]["persona"] = "everyone"
        self.assertTrue(any("persona" in e for e in self.errors()))

    def test_em_dash(self):
        self.camp["ads"][0]["copy"]["intro"] = "Pipeline \u2014 fast."
        self.assertTrue(any("em dash" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
