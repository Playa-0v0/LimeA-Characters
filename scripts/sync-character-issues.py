"""为已收录的角色建立或找回讨论议题，并以乐观并发方式更新映射。"""

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import quote, urlencode

ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
ARCHIVE = re.compile(r"^[a-zA-Z0-9._/-]+\.limea$")
HASH = re.compile(r"^[a-f0-9]{64}$")
MARKER = re.compile(r"^<!-- limea-character-id: ([a-z0-9][a-z0-9._-]{0,127}) -->$", re.MULTILINE)
MAX_CATALOG = 1024 * 1024
MAX_ARCHIVE = 32 * 1024 * 1024


class ApiError(RuntimeError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class GitHub:
    """复用 GitHub 官方 gh 命令行，不将令牌或评论内容传入命令行。"""

    def __init__(self):
        self.last_write = 0.0

    def request(self, method, path, payload=None, paginate=False):
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            delay = 1 - (time.monotonic() - self.last_write)
            if delay > 0:
                time.sleep(delay)
            self.last_write = time.monotonic()
        command = ["gh", "api", "--method", method]
        if paginate:
            command += ["--paginate", "--slurp"]
        if payload is not None:
            command += ["--input", "-"]
        command.append(path)
        result = subprocess.run(
            command,
            input=None if payload is None else json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
        )
        if result.returncode:
            match = re.search(r"\(HTTP (\d{3})\)", result.stderr)
            raise ApiError(int(match.group(1)) if match else 0, result.stderr.strip())
        return json.loads(result.stdout) if result.stdout.strip() else None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 字段重复：{key}")
        result[key] = value
    return result


def parse_json(raw, label):
    if len(raw) > MAX_CATALOG:
        raise ValueError(f"{label} 超过 1 MiB")
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} 不是有效的 UTF-8 JSON") from error


def check_issue_map(value):
    if not isinstance(value, dict) or set(value) != {"version", "issues"} or type(value["version"]) is not int or value["version"] != 1 or not isinstance(value["issues"], dict):
        raise ValueError("community.json 格式无效")
    if len(value["issues"]) > 5000:
        raise ValueError("community.json 角色数量超过限制")
    for key, number in value["issues"].items():
        if not isinstance(key, str) or not ID.fullmatch(key) or type(number) is not int or not 1 <= number <= 2147483647:
            raise ValueError("community.json 含无效的角色标识或议题编号")
    return value["issues"]


def file_from_checkout(root, archive):
    if not isinstance(archive, str) or len(archive) > 240 or not ARCHIVE.fullmatch(archive):
        raise ValueError("角色卡路径无效")
    pieces = archive.split("/")
    if any(not part or part in (".", "..") for part in pieces):
        raise ValueError("角色卡路径无效")
    path = root
    for piece in pieces:
        path = path / piece
        if path.is_symlink():
            raise ValueError(f"角色卡路径不能包含符号链接：{archive}")
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE:
        raise ValueError(f"角色卡不存在或超过大小限制：{archive}")
    return path


def read_characters(root):
    raw = (root / "catalog.json").read_bytes()
    catalog = parse_json(raw, "catalog.json")
    if not isinstance(catalog, dict) or type(catalog.get("version")) is not int or catalog["version"] != 1 or not isinstance(catalog.get("works"), list) or len(catalog["works"]) > 100:
        raise ValueError("catalog.json 格式无效")
    characters = {}
    works = set()
    for work in catalog["works"]:
        if not isinstance(work, dict):
            raise ValueError("作品格式无效")
        work_id, work_name, entries = work.get("id"), work.get("name"), work.get("characters")
        if not isinstance(work_id, str) or not ID.fullmatch(work_id) or work_id in works or not isinstance(work_name, str) or not work_name.strip() or len(work_name.strip()) > 80 or not isinstance(entries, list) or len(entries) > 500:
            raise ValueError("作品标识、名称或角色列表无效")
        works.add(work_id)
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("角色格式无效")
            character_id, name = entry.get("id"), entry.get("name")
            archive, digest = entry.get("archive"), entry.get("sha256")
            if not isinstance(character_id, str) or not ID.fullmatch(character_id) or character_id in characters or not isinstance(name, str) or not name.strip() or len(name.strip()) > 80 or not isinstance(digest, str) or not HASH.fullmatch(digest):
                raise ValueError("角色标识、名称或摘要无效")
            if not isinstance(archive, str) or not archive.startswith(work_id + "/"):
                raise ValueError(f"角色卡不在作品目录中：{character_id}")
            path = file_from_checkout(root, archive)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"角色卡摘要不匹配：{character_id}")
            try:
                with zipfile.ZipFile(path) as card:
                    manifests = [info for info in card.infolist() if info.filename == "character.json"]
                    if len(manifests) != 1 or manifests[0].file_size > MAX_CATALOG:
                        raise ValueError(f"角色卡清单无效：{character_id}")
                    manifest = parse_json(card.read(manifests[0]), "character.json")
            except (zipfile.BadZipFile, RuntimeError, OSError) as error:
                raise ValueError(f"角色卡无法读取：{character_id}") from error
            if not isinstance(manifest, dict) or manifest.get("format") != "limea-character" or type(manifest.get("formatVersion")) is not int or manifest.get("formatVersion") != 1 or manifest.get("id") != character_id or manifest.get("name") != name:
                raise ValueError(f"角色卡身份与商店清单不一致：{character_id}")
            characters[character_id] = {"name": name.strip(), "work": work_name.strip(), "archive": archive}
    return raw, characters


def get_file(api, repo, path, branch):
    try:
        result = api.request("GET", f"repos/{repo}/contents/{path}?" + urlencode({"ref": branch}))
    except ApiError as error:
        if error.status == 404:
            return None, None
        raise
    if not isinstance(result, dict) or result.get("type") != "file" or result.get("encoding") != "base64" or not isinstance(result.get("sha"), str) or not isinstance(result.get("content"), str):
        raise ValueError(f"无法读取仓库文件：{path}")
    try:
        content = base64.b64decode(result["content"].replace("\n", ""), validate=True)
    except ValueError as error:
        raise ValueError(f"仓库文件编码无效：{path}") from error
    if len(content) > MAX_CATALOG:
        raise ValueError(f"仓库文件超过大小限制：{path}")
    return content, result["sha"]


def load_mapping(api, repo, branch):
    raw, sha = get_file(api, repo, "community.json", branch)
    return ({} if raw is None else check_issue_map(parse_json(raw, "community.json"))), sha


def existing_issues(api, repo, needed):
    query = urlencode({"state": "all", "creator": "github-actions[bot]", "per_page": 100})
    pages = api.request("GET", f"repos/{repo}/issues?{query}", paginate=True)
    if not isinstance(pages, list):
        raise ValueError("议题列表格式无效")
    found = {}
    for page in pages:
        if not isinstance(page, list):
            raise ValueError("议题分页格式无效")
        for issue in page:
            if not isinstance(issue, dict) or issue.get("pull_request") or (issue.get("user") or {}).get("login") != "github-actions[bot]":
                continue
            matches = MARKER.findall(issue.get("body") or "")
            for character_id in set(matches):
                if character_id not in needed:
                    continue
                number = issue.get("number")
                if type(number) is not int or not 1 <= number <= 2147483647:
                    raise ValueError("已有议题编号无效")
                if character_id in found and found[character_id] != number:
                    raise ValueError(f"角色存在多个自动创建的议题：{character_id}")
                found[character_id] = number
    return found


def sync(api, repo, branch, root, log=print):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or branch != "main":
        raise ValueError("仓库或分支无效")
    catalog_raw, characters = read_characters(root)
    mapping, _ = load_mapping(api, repo, branch)
    missing = {key for key in characters if key not in mapping}
    if not missing:
        log("所有角色都已关联议题")
        return
    if len(mapping) + len(missing) > 5000:
        raise ValueError("角色议题映射数量超过限制")
    found = existing_issues(api, repo, missing)
    additions = {}
    for character_id in sorted(missing):
        if character_id in found:
            number = found[character_id]
            log(f"找回已有议题：{character_id} -> #{number}")
        else:
            character = characters[character_id]
            safe_name = re.sub(r"[\x00-\x1f\x7f@]+", " ", character["name"]).strip()
            if not safe_name:
                raise ValueError("角色名称不能仅包含控制字符")
            link = f"https://github.com/{repo}/blob/{branch}/{quote(character['archive'], safe='/')}"
            body = f"这个议题用于讨论 LimeA 角色卡。欢迎分享使用体验、反馈问题，或为角色点赞。\n\n角色标识：`{character_id}`\n\n[查看角色卡]({link})\n\n<!-- limea-character-id: {character_id} -->\n"
            issue = api.request("POST", f"repos/{repo}/issues", {"title": f"角色讨论：{safe_name}", "body": body})
            number = issue.get("number") if isinstance(issue, dict) else None
            if type(number) is not int or not 1 <= number <= 2147483647:
                raise ValueError("创建议题未返回有效编号，请重跑以核对")
            log(f"已创建议题：{character_id} -> #{number}")
        additions[character_id] = number
    # 在角色发生并发修改时停止；下一次运行从已有议题的标记恢复。
    latest_catalog, _ = get_file(api, repo, "catalog.json", branch)
    if latest_catalog != catalog_raw:
        raise ValueError("角色清单已变化，请重新运行以核对")
    for _ in range(3):
        latest, sha = load_mapping(api, repo, branch)
        merged = dict(latest)
        for character_id, number in additions.items():
            merged.setdefault(character_id, number)
        if merged == latest:
            log("议题映射已由其他操作写入")
            return
        check_issue_map({"version": 1, "issues": merged})
        content = (json.dumps({"version": 1, "issues": merged}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if len(content) > MAX_CATALOG:
            raise ValueError("community.json 超过大小限制")
        payload = {"message": "chore(角色商店): 更新角色议题映射", "content": base64.b64encode(content).decode("ascii"), "branch": branch}
        if sha is not None:
            payload["sha"] = sha
        try:
            api.request("PUT", f"repos/{repo}/contents/community.json", payload)
            log("已更新角色议题映射")
            return
        except ApiError as error:
            if error.status != 409 and not (error.status == 422 and "sha" in str(error).lower()):
                raise
    raise ValueError("议题映射多次发生冲突，请重跑")


if __name__ == "__main__":
    try:
        sync(GitHub(), os.environ["GITHUB_REPOSITORY"], "main", Path.cwd())
    except (ApiError, KeyError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"角色议题同步失败：{error}", file=sys.stderr)
        sys.exit(1)
