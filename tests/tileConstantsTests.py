import unittest
import engine
from engine.tileConstants import *

class MyTestCase(unittest.TestCase):
    def test_neutralizeRoad(self):
        tile = ROADS5
        tile_after = ((tile - ROADBASE) & 0xf) + ROADBASE
        tile = neutralizeRoad(tile)
        self.assertEqual(tile, tile_after, "Neutralize Test")

    def test_isRubble(self):
        tile = 44
        while tile <= 47:
            self.assertTrue(isRubble(tile))
            tile += 1
        tile = 48
        self.assertFalse(isRubble(tile))

    def test_isIndestructible(self):
        pass

if __name__ == '__main__':
    unittest.main()
