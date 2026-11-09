"""Check configuration errors and maze invariants without UI snapshots."""

from collections import deque
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.mazegen.generator import MazeGenerator

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = {"N": (0, -1, 1, 4), "E": (1, 0, 2, 8),
              "S": (0, 1, 4, 1), "W": (-1, 0, 8, 2)}
PATTERN = ("1010111", "1010001", "1110111", "0010100", "0010111")


class MazeTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = tempfile.TemporaryDirectory(prefix="maze-test-")
        self.addCleanup(workspace.cleanup)
        self.work = Path(workspace.name)

    def config(self, **changes: str) -> str:
        values = {"WIDTH": "20", "HEIGHT": "15", "ENTRY": "0,0",
                  "EXIT": "19,14", "OUTPUT_FILE": "maze.txt",
                  "PERFECT": "True", "SEED": "42"}
        values.update(changes)
        return "# test configuration\n" + "".join(
            f"{key}={value}\n" for key, value in values.items())

    def call(self, text: str) -> subprocess.CompletedProcess[str]:
        (self.work / "config.txt").write_text(text)
        return subprocess.run(
            [sys.executable, str(ROOT / "a_maze_ing.py"), "config.txt"],
            cwd=self.work, input="4\n", capture_output=True, text=True,
            timeout=8)

    def verify(self, width: int, height: int, perfect: bool) -> bytes:
        file = self.work / "maze.txt"
        data = file.read_bytes()
        self.assertTrue(data.endswith(b"\n"))
        lines = data.decode().splitlines()
        self.assertEqual(len(lines), height + 4)
        self.assertEqual(lines[height], "")
        grid: list[list[int]] = []
        for line in lines[:height]:
            self.assertEqual(len(line), width)
            self.assertRegex(line, r"^[0-9a-fA-F]+$")
            grid.append([int(char, 16) for char in line])
        entry = tuple(map(int, lines[height + 1].split(",")))
        exit_pos = tuple(map(int, lines[height + 2].split(",")))
        self.assertEqual(entry, (0, 0))
        self.assertEqual(exit_pos, (width - 1, height - 1))
        blocked = set()
        if width >= 7 and height >= 5:
            for y, row in enumerate(PATTERN):
                for x, cell in enumerate(row):
                    if cell == "1":
                        blocked.add(((width - 7) // 2 + x,
                                     (height - 5) // 2 + y))
        nodes = {(x, y) for y in range(height) for x in range(width)} - blocked
        for y in range(height):
            for x in range(width):
                for dx, dy, bit, opposite in DIRECTIONS.values():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        self.assertEqual(bool(grid[y][x] & bit),
                                         bool(grid[ny][nx] & opposite))
                    else:
                        self.assertTrue(grid[y][x] & bit)
                if (x, y) in blocked:
                    self.assertEqual(grid[y][x], 15)
        distance: dict[tuple[int, int], int] = {(0, 0): 0}
        queue = deque([(0, 0)])
        edges = 0
        while queue:
            x, y = queue.popleft()
            for dx, dy, bit, _ in DIRECTIONS.values():
                if not grid[y][x] & bit:
                    edges += 1
                    neighbor = (x + dx, y + dy)
                    if neighbor not in distance:
                        distance[neighbor] = distance[x, y] + 1
                        queue.append(neighbor)
        self.assertEqual(set(distance), nodes)
        if perfect:
            self.assertEqual(edges // 2, len(nodes) - 1)
        else:
            self.assertGreaterEqual(edges // 2 - len(nodes) + 1, 2)
        x = y = 0
        path = lines[-1]
        for direction in path:
            self.assertIn(direction, DIRECTIONS)
            dx, dy, bit, _ = DIRECTIONS[direction]
            self.assertFalse(grid[y][x] & bit)
            x, y = x + dx, y + dy
            self.assertIn((x, y), nodes)
        self.assertEqual((x, y), exit_pos)
        self.assertEqual(len(path), distance[width - 1, height - 1])
        return data

    def test_valid_output_and_both_generation_modes(self) -> None:
        algorithms = ["Kruskal"]
        if (ROOT / "src/mazegen/parser.py").exists():
            algorithms.append("DFS")
        for algorithm in algorithms:
            for perfect in (True, False):
                with self.subTest(algorithm=algorithm, perfect=perfect):
                    result = self.call(self.config(
                        ALGORITHM=algorithm, PERFECT=str(perfect)))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.verify(20, 15, perfect)

    def test_seed_is_reproducible(self) -> None:
        text = self.config()
        self.assertEqual(self.call(text).returncode, 0)
        first = self.verify(20, 15, True)
        self.assertEqual(self.call(text).returncode, 0)
        self.assertEqual(self.verify(20, 15, True), first)

    def test_minimal_maze_and_missing_42_warning(self) -> None:
        result = self.call(self.config(WIDTH="2", HEIGHT="1", EXIT="1,0"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.verify(2, 1, True)
        self.assertIn("42", result.stdout + result.stderr)

    def test_generator_can_be_reused(self) -> None:
        generator = MazeGenerator(20, 15, 42)
        generator.generate(perfect=True)
        grid = generator.generate(perfect=True)
        self.assertTrue(all(0 <= cell <= 15 for row in grid for cell in row))

    def test_invalid_configuration_is_rejected(self) -> None:
        valid = self.config()
        cases = [valid.replace("WIDTH=20\n", ""),
                 valid + "WIDTH=20\n", valid + "broken line\n",
                 self.config(WIDTH="0"), self.config(HEIGHT="-1"),
                 self.config(WIDTH="abc"), self.config(PERFECT="maybe"),
                 self.config(ENTRY="-1,0"), self.config(ENTRY="20,0"),
                 self.config(EXIT="0"), self.config(SEED="abc")]
        for text in cases:
            with self.subTest(config=text):
                result = self.call(text)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_identical_or_blocked_endpoints_are_rejected(self) -> None:
        for entry in ("19,14", "6,5"):
            with self.subTest(entry=entry):
                result = self.call(self.config(ENTRY=entry))
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_missing_input_and_output_directory(self) -> None:
        for args in ([], ["missing.txt"], ["a", "b"]):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "a_maze_ing.py"), *args],
                    cwd=self.work, input="4\n", text=True,
                    capture_output=True, timeout=5)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
        result = self.call(self.config(OUTPUT_FILE="missing/maze.txt"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
