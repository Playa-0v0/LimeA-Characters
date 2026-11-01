import assert from "node:assert/strict";
import test from "node:test";
import {
  mkdtemp,
  mkdir,
  writeFile,
  readFile,
  rm,
  readdir,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import sharp from "sharp";
import { buildCharacters } from "../scripts/build-characters.mjs";

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "limea-character-build-"));
  await mkdir(join(root, "new-work/characters_dev/new-role/assets"), {
    recursive: true,
  });
  await mkdir(join(root, "icons"));
  const image = await sharp({
    create: { width: 24, height: 32, channels: 3, background: "#aabbcc" },
  })
    .webp()
    .toBuffer();
  await writeFile(join(root, "icons/new-work.webp"), image);
  await writeFile(
    join(root, "new-work/characters_dev/new-role/assets/avatar.webp"),
    image,
  );
  await writeFile(
    join(root, "works.json"),
    JSON.stringify({
      version: 1,
      works: [
        {
          id: "new-work",
          name: "全新作品",
          icon: { path: "icons/new-work.webp" },
        },
      ],
    }),
  );
  await writeFile(
    join(root, "README.md"),
    "# 角色\n\n<!-- characters:start -->\n\n<!-- characters:end -->\n",
  );
  await writeFile(join(root, "community.json"), "keep-community\n");
  const manifest = {
    format: "limea-character",
    formatVersion: 1,
    id: "org.example.new-role",
    version: "1.0.0",
    name: "新角色",
    extensions: { "limea.work": { id: "new-work", name: "全新作品" } },
    files: [{ path: "assets/avatar.webp", role: "avatar" }],
  };
  await writeFile(
    join(root, "new-work/characters_dev/new-role/character.json"),
    JSON.stringify(manifest),
  );
  return root;
}
async function cleanup(root) {
  assert.ok(
    resolve(root).startsWith(resolve(join(tmpdir(), "limea-character-build-"))),
  );
  await rm(root, { recursive: true, force: true });
}

test("不同本机时区生成相同的角色包和清单", async () => {
  const root = await fixture();
  const previous = process.env.TZ;
  try {
    process.env.TZ = "Asia/Shanghai";
    await buildCharacters(root);
    const original = await readFile(
      join(root, "new-work/characters/new-role/new-role.limea"),
    );
    for (const timezone of ["Etc/UTC", "America/New_York"]) {
      process.env.TZ = timezone;
      await buildCharacters(root, true);
      await buildCharacters(root);
      assert.deepEqual(
        await readFile(
          join(root, "new-work/characters/new-role/new-role.limea"),
        ),
        original,
      );
    }
  } finally {
    if (previous === undefined) delete process.env.TZ;
    else process.env.TZ = previous;
    await cleanup(root);
  }
});
test("新增作品只需数据声明，构建和校验稳定且保持讨论映射", async () => {
  const root = await fixture();
  try {
    await buildCharacters(root);
    const first = await readFile(
      join(root, "new-work/characters/new-role/new-role.limea"),
    );
    await buildCharacters(root);
    await buildCharacters(root, true);
    assert.deepEqual(
      await readFile(join(root, "new-work/characters/new-role/new-role.limea")),
      first,
    );
    assert.deepEqual(
      (await readdir(join(root, "new-work/characters/new-role"))).sort(),
      ["avatar.webp", "new-role.limea"],
    );
    assert.equal(
      JSON.parse(await readFile(join(root, "works.json"), "utf8")).works[0].icon
        .sha256.length,
      64,
    );
    assert.equal(
      await readFile(join(root, "community.json"), "utf8"),
      "keep-community\n",
    );
    const readme = await readFile(join(root, "README.md"), "utf8");
    assert.match(readme, /全新作品/);
    assert.equal((readme.match(/<table>/g) ?? []).length, 1);
    assert.match(readme, /<\/table>/);
    await writeFile(
      join(root, "new-work/characters/new-role/new-role.limea"),
      "tampered",
    );
    await assert.rejects(buildCharacters(root, true), /生成文件过期/);
  } finally {
    await cleanup(root);
  }
});
test("拒绝错误作品归属、未声明文件和重复作品，失败时不输出正式文件", async () => {
  const root = await fixture();
  try {
    const path = join(root, "new-work/characters_dev/new-role/character.json");
    const manifest = JSON.parse(await readFile(path, "utf8"));
    await writeFile(
      path,
      JSON.stringify({
        ...manifest,
        extensions: { "limea.work": { id: "other-work", name: "全新作品" } },
      }),
    );
    await assert.rejects(buildCharacters(root), /作品声明/);
    await assert.rejects(readFile(join(root, "catalog.json")));
    await writeFile(path, JSON.stringify(manifest));
    await writeFile(
      join(root, "new-work/characters_dev/new-role/extra.md"),
      "undeclared",
    );
    await assert.rejects(buildCharacters(root), /未声明/);
    await rm(join(root, "new-work/characters_dev/new-role/extra.md"));
    const registry = JSON.parse(
      await readFile(join(root, "works.json"), "utf8"),
    );
    registry.works.push({ ...registry.works[0] });
    await writeFile(join(root, "works.json"), JSON.stringify(registry));
    await assert.rejects(buildCharacters(root), /作品标识/);
  } finally {
    await cleanup(root);
  }
});
