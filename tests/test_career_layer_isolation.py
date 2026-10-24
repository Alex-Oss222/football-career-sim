"""The career layer never reaches what resolves a game.

The career layer is the job record, the decision queue, the career views
and every runtime module listed in ``LAYER`` (a module that imports one of
them, or reads the event store, the queue or the job record; rebuild step 5
adds the event, insert, response, deadline, bye, transaction and league-coach
modules). No runtime module outside ``LAYER`` imports a career-layer module
(an AST scan of every runtime/*.py, so a module added later is covered).
The weekly scripts import the queue only inside main(), never in
close_slate, write_receipts or anywhere else a game is drawn or a receipt
written, and importing the game modules and both weekly scripts loads no
career-layer module (docs/career_layer.md). Each new runtime module outside
the layer (``OUTSIDE``) loads none on its own, in a fresh interpreter.
"""
import ast
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAYER = {"current_job.py", "decision_queue.py",
         # Rebuild step 5: the event store and clock, the inserts, My Responses, the deadlines,
         # the bye, the roster transactions and the league's head-coach changes.
         "open_events.py", "event_inserts.py", "responses.py", "deadlines.py", "bye_week.py",
         "transactions.py", "league_coaches.py"}
CAREER = tuple(sorted("runtime." + name[:-len(".py")] for name in LAYER)) + ("scripts.render_career_views",)
# New runtime modules outside the layer: they take events, queue items and results as arguments.
OUTSIDE = ("practices", "player_contracts")
# Named so a rename cannot leave the scan silently empty.
GAME_MODULES = ("week_inputs", "game_runner", "kernel", "private_service", "private_client",
                "statbook", "observables", "defensive_calls")
WEEKLY_SCRIPTS = ("scripts/close_week.py", "scripts/build_week_inputs.py")


def imported(node, package):
    """The fully qualified names an import statement loads."""
    if isinstance(node, ast.Import):
        return {alias.name for alias in node.names}
    parts = package.split(".")
    base = ".".join(parts[:len(parts) - node.level + 1]) if node.level else ""
    module = ".".join(p for p in (base, node.module) if p)
    return {module} | {module + "." + alias.name for alias in node.names}


def career_imports(tree, package):
    """Every import node in ``tree`` that loads a career-layer module."""
    return [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
            and any(name == c or name.startswith(c + ".") for name in imported(node, package) for c in CAREER)]


def parse(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class CareerLayerIsolationTests(unittest.TestCase):
    def test_no_runtime_module_imports_the_career_layer(self):
        scanned = [p for p in sorted((ROOT / "runtime").glob("*.py")) if p.name not in LAYER]
        self.assertTrue({m + ".py" for m in GAME_MODULES} <= {p.name for p in scanned})
        found = ["%s:%d" % (p.relative_to(ROOT), node.lineno)
                 for p in scanned for node in career_imports(parse(p), "runtime")]
        self.assertEqual(found, [])

    def test_weekly_scripts_import_the_queue_only_inside_main(self):
        for relative in WEEKLY_SCRIPTS:
            with self.subTest(script=relative):
                tree = parse(ROOT / relative)
                main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
                inside = {id(n) for n in ast.walk(main)}
                found = career_imports(tree, "scripts")
                # The gate is wired, and only main() reaches it.
                self.assertTrue(found)
                self.assertEqual(["line %d" % n.lineno for n in found if id(n) not in inside], [])
        close_week = parse(ROOT / "scripts/close_week.py")
        for name in ("close_slate", "write_receipts"):
            function = next(n for n in close_week.body if isinstance(n, ast.FunctionDef) and n.name == name)
            self.assertEqual(career_imports(function, "scripts"), [], name)

    def test_importing_the_game_modules_loads_no_career_module(self):
        modules = ["runtime." + p.stem for p in sorted((ROOT / "runtime").glob("*.py"))
                   if p.name not in LAYER and p.stem != "__init__"]
        code = ("import importlib, sys\n"
                "for name in sys.argv[1:]:\n"
                "    importlib.import_module(name)\n"
                "print(sorted(m for m in sys.modules if m in %r))" % (CAREER,))
        done = subprocess.run([sys.executable, "-c", code, *modules, "scripts.build_week_inputs",
                               "scripts.close_week"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), "[]")

    def test_each_new_module_outside_the_layer_loads_no_career_module(self):
        code = ("import importlib, sys\n"
                "importlib.import_module(sys.argv[1])\n"
                "print(sorted(m for m in sys.modules if m in %r))" % (CAREER,))
        for name in OUTSIDE:
            with self.subTest(module=name):
                path = ROOT / "runtime" / (name + ".py")
                self.assertTrue(path.is_file(), path)
                self.assertNotIn(path.name, LAYER)
                # Nothing from the layer at module level or inside a function.
                self.assertEqual(career_imports(parse(path), "runtime"), [])
                done = subprocess.run([sys.executable, "-c", code, "runtime." + name], cwd=ROOT,
                                      capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertEqual(done.stdout.strip(), "[]")


if __name__ == "__main__":
    unittest.main()
