import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import postseason
from scripts.render_season_stats import load_receipts

ROOT = Path(__file__).resolve().parents[1]


def slot(conference, matchup, day, time="13:00", **extra):
    return {"conference": conference, "matchup": matchup, "date": day, "kickoff_et": time, **extra}


SLOTS = {
    "super_bowl_matchup": "NFC@AFC", "designated_home_conference": "AFC",
    "rounds": [
        {"week": 18, "slots": [slot("AFC", "5@4", "2014-01-04", "16:35"), slot("NFC", "6@3", "2014-01-04", "20:10"),
                               slot("AFC", "6@3", "2014-01-05", "13:05"), slot("NFC", "5@4", "2014-01-05", "16:40")]},
        {"week": 19, "slots": [slot("NFC", "low@1", "2014-01-11", "16:35"), slot("AFC", "other@2", "2014-01-11", "20:15"),
                               slot("NFC", "other@2", "2014-01-12", "13:05"), slot("AFC", "low@1", "2014-01-12", "16:40")]},
        {"week": 20, "slots": [slot("AFC", "lower@higher", "2014-01-19", "15:00"),
                               slot("NFC", "lower@higher", "2014-01-19", "18:30")]},
        {"week": 21, "slots": [slot("NFL", "NFC@AFC", "2014-02-02", "18:30", site="neutral", venue="MetLife Stadium")]},
    ],
}


def result(week, away, home, away_points, home_points):
    return {"week": week, "away": away, "home": home, "event_id": "%d-%s-%s" % (week, away, home),
            "final_score": {away: away_points, home: home_points}}


class PostseasonBracketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regular = load_receipts(ROOT / "career/2013/stats/game_receipts")
        cls.field = postseason.seeds(cls.regular)

    def games(self, week, post):
        return postseason.schedule(week, self.regular, post, SLOTS)

    def test_field_is_six_per_conference(self):
        self.assertEqual({c: len(t) for c, t in self.field.items()}, {"AFC": 6, "NFC": 6})

    def test_wild_card_pairs_3v6_and_4v5_with_the_higher_seed_home(self):
        wc = self.games(18, [])
        self.assertEqual(len(wc), 4)
        for game in wc:
            self.assertLess(game["home_seed"], game["away_seed"])
            self.assertEqual(game["game_type"], "postseason")
        afc = self.field["AFC"]
        self.assertIn((afc[4], afc[3]), [(g["away"], g["home"]) for g in wc])
        first = wc[0]
        self.assertEqual((first["date"], first["kickoff_et"], first["matchup"]), ("2014-01-04", "16:35", "5@4"))

    def test_next_round_waits_for_every_closed_game(self):
        with self.assertRaises(ValueError):
            self.games(19, [])

    def test_divisional_reseeds_and_later_rounds_follow(self):
        afc, nfc = self.field["AFC"], self.field["NFC"]
        # Road teams win every Wild Card game: the 5 and 6 seeds advance.
        post = [result(18, g["away"], g["home"], 20, 17) for g in self.games(18, [])]
        div = {(g["conference"], g["matchup"]): g for g in self.games(19, post)}
        self.assertEqual((div["AFC", "low@1"]["away"], div["AFC", "low@1"]["home"]), (afc[5], afc[0]))
        self.assertEqual((div["AFC", "other@2"]["away"], div["AFC", "other@2"]["home"]), (afc[4], afc[1]))
        # Home teams win the Divisional round: seeds 1 and 2 meet, 1 hosts.
        post += [result(19, g["away"], g["home"], 10, 24) for g in div.values()]
        conf = {g["conference"]: g for g in self.games(20, post)}
        self.assertEqual((conf["AFC"]["away"], conf["AFC"]["home"]), (afc[1], afc[0]))
        self.assertEqual((conf["NFC"]["away"], conf["NFC"]["home"]), (nfc[1], nfc[0]))
        post += [result(20, g["away"], g["home"], 30, 27) for g in conf.values()]
        (sb,) = self.games(21, post)
        self.assertEqual((sb["away"], sb["home"], sb["site"]), (nfc[1], afc[1], "neutral"))

    def test_a_tied_postseason_receipt_is_rejected(self):
        with self.assertRaises(ValueError):
            postseason.winner(result(18, "A", "B", 17, 17))


if __name__ == "__main__":
    unittest.main()
