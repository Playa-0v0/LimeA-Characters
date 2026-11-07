import base64
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("character_issues", ROOT / "scripts" / "sync-character-issues.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FakeGitHub:
    def __init__(self, catalog, mapping=None, gitcode_mapping=None, issues=None):
        self.catalog = catalog
        self.mapping = mapping
        self.gitcode_mapping = gitcode_mapping
        self.issues = issues or []
        self.created = []
        self.writes = 0
        self.conflict = None
        self.fail_write = False

    def request(self, method, path, payload=None, paginate=False):
        if method == "GET" and path.startswith("repos/example/repo/contents/catalog.json?"):
            return self.file(self.catalog)
        for filename, attribute in (
            ("community.json", "mapping"),
            ("community-gitcode.json", "gitcode_mapping"),
        ):
            if method == "GET" and path.startswith(f"repos/example/repo/contents/{filename}?"):
                mapping = getattr(self, attribute)
                if mapping is None:
                    raise module.ApiError(404, "missing")
                return self.file(json.dumps({"version": 1, "issues": mapping}).encode())
            if method == "PUT" and path == f"repos/example/repo/contents/{filename}":
                self.writes += 1
                if self.fail_write:
                    self.fail_write = False
                    raise module.ApiError(500, "interrupted")
                if self.conflict is not None:
                    setattr(self, attribute, self.conflict)
                    self.conflict = None
                    raise module.ApiError(409, "conflict")
                parsed = json.loads(base64.b64decode(payload["content"]))
                setattr(self, attribute, parsed["issues"])
                return {}
        if method == "GET" and path.startswith("repos/example/repo/issues?"):
            if not paginate:
                raise AssertionError("缺少分页")
            return [self.issues.copy()]
        if method == "POST" and path == "repos/example/repo/issues":
            number = len(self.issues) + 1
            issue = {"number": number, "user": {"login": "github-actions[bot]"}, "body": payload["body"]}
            self.issues.append(issue)
            self.created.append(payload)
            return issue
        raise AssertionError((method, path))

    @staticmethod
    def file(raw):
        return {"type": "file", "encoding": "base64", "sha": hashlib.sha1(raw).hexdigest(), "content": base64.b64encode(raw).decode()}


class FakeGitCode:
    def __init__(self, actor="gitcode-bot", issues=None):
        self.actor = actor
        self.issue_list = issues or []
        self.created = []

    def issues(self, repo):
        if repo != "example/repo":
            raise AssertionError(repo)
        return self.issue_list.copy()

    def create_issue(self, repo, title, body):
        number = len(self.issue_list) + 1
        issue = {"number": number, "user": {"login": self.actor}, "title": title, "body": body}
        self.issue_list.append(issue)
        self.created.append({"title": title, "body": body})
        return issue


class IssueSyncTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="limea-character-issues-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "game").mkdir()
        with zipfile.ZipFile(self.root / "game" / "character.limea", "w") as card:
            card.writestr("character.json", json.dumps({"format": "limea-character", "formatVersion": 1, "id": "test.character", "name": "测试角色"}, ensure_ascii=False))
        digest = hashlib.sha256((self.root / "game" / "character.limea").read_bytes()).hexdigest()
        self.catalog = {"version": 1, "works": [{"id": "game", "name": "作品", "characters": [{"id": "test.character", "name": "测试角色", "archive": "game/character.limea", "sha256": digest}]}]}
        self.raw = (json.dumps(self.catalog, ensure_ascii=False) + "\n").encode()
        (self.root / "catalog.json").write_bytes(self.raw)
        self.api = FakeGitHub(self.raw)

    def sync(self):
        module.sync(self.api, "example/repo", "main", self.root, log=lambda *args: None)

    def test_create_mapping_and_repeat_without_duplicate(self):
        self.sync()
        self.assertEqual(self.api.mapping, {"test.character": 1})
        self.assertIn("<!-- limea-character-id: test.character -->", self.api.created[0]["body"])
        self.assertEqual(self.api.created[0]["title"], "角色讨论：测试角色")
        self.sync()
        self.assertEqual(len(self.api.created), 1)
        self.assertEqual(self.api.writes, 1)

    def test_recover_after_issue_created_but_mapping_write_failed(self):
        self.api.fail_write = True
        with self.assertRaises(module.ApiError):
            self.sync()
        self.assertEqual(len(self.api.created), 1)
        self.assertIsNone(self.api.mapping)
        self.sync()
        self.assertEqual(len(self.api.created), 1)
        self.assertEqual(self.api.mapping, {"test.character": 1})

    def test_preserve_existing_mapping_and_retry_concurrent_update(self):
        self.api.mapping = {"older.character": 99}
        self.api.conflict = {"older.character": 99, "other.character": 77}
        self.sync()
        self.assertEqual(self.api.mapping, {"older.character": 99, "other.character": 77, "test.character": 1})
        self.assertEqual(self.api.writes, 2)

    def test_do_not_overwrite_mapping_added_by_other_writer(self):
        self.api.conflict = {"test.character": 45}
        self.sync()
        self.assertEqual(self.api.mapping, {"test.character": 45})
        self.assertEqual(self.api.writes, 1)

    def test_changed_catalog_stops_write_and_next_run_reuses_issue(self):
        self.api.catalog = b"changed"
        with self.assertRaisesRegex(ValueError, "清单已变化"):
            self.sync()
        self.assertIsNone(self.api.mapping)
        self.api.catalog = self.raw
        self.sync()
        self.assertEqual(len(self.api.created), 1)
        self.assertEqual(self.api.mapping, {"test.character": 1})

    def test_reject_invalid_archive_or_identity_before_creating_issue(self):
        (self.root / "game" / "character.limea").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "摘要不匹配"):
            self.sync()
        self.assertEqual(self.api.created, [])

    def test_duplicate_bot_issues_require_manual_resolution(self):
        marker = "<!-- limea-character-id: test.character -->"
        self.api.issues = [{"number": n, "user": {"login": "github-actions[bot]"}, "body": marker} for n in (1, 2)]
        with self.assertRaisesRegex(ValueError, "多个"):
            self.sync()
        self.assertEqual(self.api.created, [])

    def test_untrusted_issue_marker_is_not_reused(self):
        self.api.issues = [{"number": 9, "user": {"login": "other-user"}, "body": "<!-- limea-character-id: test.character -->"}]
        self.sync()
        self.assertEqual(self.api.mapping, {"test.character": 2})
        self.assertEqual(len(self.api.created), 1)

    def test_other_422_errors_are_not_retried(self):
        original = self.api.request
        attempts = []
        def request(method, path, payload=None, paginate=False):
            if method == "PUT":
                attempts.append(1)
                raise module.ApiError(422, "Validation failed, or the endpoint has been spammed")
            return original(method, path, payload, paginate)
        self.api.request = request
        with self.assertRaises(module.ApiError):
            self.sync()
        self.assertEqual(len(attempts), 1)

    def test_invalid_existing_mapping_is_never_overwritten(self):
        self.api.mapping = {"test.character": 0}
        with self.assertRaisesRegex(ValueError, "议题编号"):
            self.sync()
        self.assertEqual(self.api.created, [])
        self.assertEqual(self.api.mapping, {"test.character": 0})


    def sync_gitcode(self, gitcode):
        module.sync_gitcode(
            self.api, gitcode, "example/repo", "main", self.root, log=lambda *args: None
        )

    def test_gitcode_creates_separate_mapping_and_issue(self):
        gitcode = FakeGitCode()
        self.sync_gitcode(gitcode)
        self.assertEqual(self.api.gitcode_mapping, {"test.character": 1})
        self.assertIsNone(self.api.mapping)
        self.assertIn("<!-- limea-character-id: test.character -->", gitcode.created[0]["body"])
        self.assertIn(
            "https://gitcode.com/example/repo/blob/main/game/character.limea",
            gitcode.created[0]["body"],
        )
        self.assertEqual(gitcode.created[0]["title"], "角色讨论：测试角色")
        self.sync_gitcode(gitcode)
        self.assertEqual(len(gitcode.created), 1)
        self.assertEqual(self.api.writes, 1)

    def test_gitcode_reuses_issue_created_before_mapping_write(self):
        gitcode = FakeGitCode()
        self.api.fail_write = True
        with self.assertRaises(module.ApiError):
            self.sync_gitcode(gitcode)
        self.assertEqual(len(gitcode.created), 1)
        self.assertIsNone(self.api.gitcode_mapping)
        self.sync_gitcode(gitcode)
        self.assertEqual(len(gitcode.created), 1)
        self.assertEqual(self.api.gitcode_mapping, {"test.character": 1})

    def test_gitcode_ignores_marker_from_other_actor(self):
        marker = "<!-- limea-character-id: test.character -->"
        gitcode = FakeGitCode(issues=[{"number": 9, "user": {"login": "other-user"}, "body": marker}])
        self.sync_gitcode(gitcode)
        self.assertEqual(self.api.gitcode_mapping, {"test.character": 2})
        self.assertEqual(len(gitcode.created), 1)


if __name__ == "__main__":
    unittest.main()
