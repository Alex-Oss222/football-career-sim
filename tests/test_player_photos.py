import unittest
from scripts.player_photos import Photos, place_block, block, PHOTO_START, PHOTO_END, credit_short


class PlayerPhotoTests(unittest.TestCase):
    def setUp(self):
        self.photos = Photos()

    def test_registry_rows_carry_a_license(self):
        self.assertGreater(len(self.photos.players), 1000)
        for row in self.photos.players.values():
            self.assertTrue(row['url'].startswith('https://commons.wikimedia.org/'))
            self.assertTrue(row['license'])

    def test_lookup_by_registry_name_and_ambiguity(self):
        row = self.photos.lookup('Kirk Cousins')
        self.assertEqual(row['name'], 'Kirk Cousins')
        self.assertIsNone(self.photos.lookup('Nobody Real'))
        # a shared name without a club to resolve it gets no photo
        shared = [n for n, ids in self.photos.by_name.items() if len(ids) > 1]
        self.assertTrue(shared)
        self.assertIsNone(self.photos.lookup(shared[0]))

    def test_block_is_idempotent_and_removable(self):
        row = self.photos.lookup('Kirk Cousins')
        text = '# Kirk Cousins — 2014 Player Profile\n\n**Team:** Jacksonville Jaguars  \n'
        once = place_block(text, row, 'Kirk Cousins')
        self.assertEqual(once.count(PHOTO_START), 1)
        self.assertTrue(once.startswith('# Kirk Cousins — 2014 Player Profile\n\n' + PHOTO_START))
        self.assertIn('**Team:** Jacksonville Jaguars', once)
        self.assertEqual(place_block(once, row, 'Kirk Cousins'), once)
        self.assertEqual(place_block(once, None, 'Kirk Cousins'), text)
        self.assertIn(PHOTO_END, block(row, 'Kirk Cousins'))
        self.assertIn(row['license'], credit_short(row))


if __name__ == '__main__':
    unittest.main()
