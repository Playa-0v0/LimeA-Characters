import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir, readdir, lstat } from "node:fs/promises";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";
import { ZipFile } from "yazl";

const idPattern = /^[a-z0-9][a-z0-9._-]{0,127}$/;
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const json = (value) => Buffer.from(JSON.stringify(value, null, 2) + "\n");
function safePath(path) {
  if (
    typeof path !== "string" ||
    path.length > 240 ||
    path.includes("\\") ||
    path
      .split("/")
      .some(
        (part) =>
          !part ||
          part === "." ||
          part === ".." ||
          /[\x00-\x1f<>:"|?*]/.test(part),
      )
  )
    throw new Error("资源路径无效");
  return path;
}
async function bytes(root, path) {
  safePath(path);
  let cursor = root;
  for (const part of path.split("/")) {
    cursor = join(cursor, part);
    if ((await lstat(cursor)).isSymbolicLink())
      throw new Error("资源不能为链接");
  }
  if ((await lstat(cursor)).size > 16 * 1024 * 1024)
    throw new Error("单个资源超过 16 MiB");
  return readFile(cursor);
}
async function filesIn(root, path) {
  const files = [];
  for (const entry of await readdir(join(root, path), {
    withFileTypes: true,
  })) {
    const name = `${path}/${entry.name}`;
    if (entry.isSymbolicLink()) throw new Error("目录不能包含链接");
    if (entry.isDirectory()) files.push(...(await filesIn(root, name)));
    else if (entry.isFile()) files.push(name);
    else throw new Error("目录不能包含特殊文件");
  }
  return files.sort();
}
async function archive(files) {
  const zip = new ZipFile();
  for (const name of [...files.keys()].sort())
    zip.addBuffer(files.get(name), name, {
      // DOS 时间按本地时区编码；固定本地日期并禁用 UTC 扩展，跨时区生成相同字节。
      mtime: new Date(2020, 0, 1),
      forceDosTimestamp: true,
      mode: 0o100644,
    });
  zip.end();
  const chunks = [];
  for await (const chunk of zip.outputStream) chunks.push(chunk);
  const result = Buffer.concat(chunks);
  if (result.length > 32 * 1024 * 1024) throw new Error("角色卡超过 32 MiB");
  return result;
}
async function preview(data, width, height) {
  const image = sharp(data, {
    limitInputPixels: 32 * 1024 * 1024,
    animated: false,
  });
  const meta = await image.metadata();
  if (!["png", "jpeg", "webp"].includes(meta.format) || (meta.pages ?? 1) > 1)
    throw new Error("预览必须使用静态图片");
  const output = await image
    .rotate()
    .resize(width, height, { fit: "cover" })
    .webp({ quality: 82 })
    .toBuffer();
  if (output.length > 1024 * 1024) throw new Error("预览超过 1 MiB");
  return output;
}
const escape = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("|", "&#124;")
    .replace(/[\r\n]+/g, " ");

/** 源码是唯一编辑入口；所有校验完成后才写出分发文件。 */
export async function buildCharacters(root, check = false) {
  const registry = JSON.parse(await readFile(join(root, "works.json"), "utf8"));
  if (
    registry.version !== 1 ||
    Object.keys(registry).some((key) => !["version", "works"].includes(key)) ||
    !Array.isArray(registry.works) ||
    registry.works.length > 500
  )
    throw new Error("作品索引无效");
  const ids = new Set();
  const characters = new Set();
  const outputs = new Map();
  const catalog = { version: 1, works: [] };
  const tables = [];
  for (const work of registry.works) {
    if (
      !work ||
      Object.keys(work).some((key) => !["id", "name", "icon"].includes(key))
    )
      throw new Error("作品索引含未知字段");
    if (
      !idPattern.test(work.id) ||
      ids.has(work.id) ||
      typeof work.name !== "string" ||
      !work.name.trim() ||
      work.name.length > 80
    )
      throw new Error("作品标识或名称无效");
    ids.add(work.id);
    if (work.icon) {
      if (
        Object.keys(work.icon).some((key) => !["path", "sha256"].includes(key))
      )
        throw new Error("图标声明含未知字段");
      if (
        !work.icon.path?.startsWith("icons/") ||
        !work.icon.path.endsWith(".webp")
      )
        throw new Error("作品图标必须在 icons 下");
      const data = await bytes(root, work.icon.path);
      const meta = await sharp(data, {
        limitInputPixels: 4_000_000,
        animated: false,
      }).metadata();
      if (
        data.length > 256 * 1024 ||
        meta.format !== "webp" ||
        (meta.pages ?? 1) > 1
      )
        throw new Error("作品图标必须为 256 KiB 内的静态 WebP");
      work.icon.sha256 = hash(data);
    }
    const sourceRoot = `${work.id}/characters_dev`;
    const names = await readdir(join(root, sourceRoot)).catch((error) => {
      if (error.code === "ENOENT") return [];
      throw error;
    });
    const entries = [];
    const rows = [];
    for (const slug of names.sort()) {
      if (!idPattern.test(slug))
        throw new Error("角色目录名必须是小写稳定标识");
      const source = `${sourceRoot}/${slug}`;
      const manifest = JSON.parse(
        (await bytes(root, `${source}/character.json`)).toString("utf8"),
      );
      if (
        manifest.format !== "limea-character" ||
        manifest.formatVersion !== 1 ||
        !idPattern.test(manifest.id) ||
        characters.has(manifest.id) ||
        !manifest.name?.trim() ||
        !/^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$/.test(manifest.version)
      )
        throw new Error("角色卡身份或版本无效");
      const declaredWork = manifest.extensions?.["limea.work"];
      if (
        Object.keys(declaredWork ?? {}).some(
          (key) => !["id", "name"].includes(key),
        ) ||
        declaredWork?.id !== work.id ||
        declaredWork.name !== work.name
      )
        throw new Error("角色卡作品声明与作品索引不一致");
      characters.add(manifest.id);
      const declarations = [
        ...(manifest.files ?? []),
        ...(manifest.prompts?.fixed ?? []).map((path) => ({ path })),
        ...(manifest.prompts?.worldbooks ?? []).map((path) => ({ path })),
      ];
      const files = new Map([
        ["character.json", await bytes(root, `${source}/character.json`)],
      ]);
      for (const file of declarations) {
        safePath(file.path);
        if (files.has(file.path)) throw new Error("角色卡文件重复声明");
        files.set(file.path, await bytes(root, `${source}/${file.path}`));
      }
      const actual = await filesIn(root, source);
      if (
        actual.length !== files.size ||
        actual.some((path) => !files.has(path.slice(source.length + 1)))
      )
        throw new Error("制作目录存在未声明文件");
      if (
        files.size > 256 ||
        [...files.values()].reduce((n, data) => n + data.length, 0) >
          64 * 1024 * 1024
      )
        throw new Error("角色卡展开容量超过限制");
      const target = `${work.id}/characters/${slug}`;
      const packagePath = `${target}/${slug}.limea`;
      const data = await archive(files);
      outputs.set(packagePath, data);
      const entry = {
        id: manifest.id,
        name: manifest.name,
        description: manifest.description ?? "",
        archive: packagePath,
        sha256: hash(data),
      };
      for (const [role, width, height] of [
        ["avatar", 192, 192],
        ["cover", 360, 480],
      ]) {
        const file = (manifest.files ?? []).find((file) => file.role === role);
        if (file) {
          const image = await preview(files.get(file.path), width, height);
          const path = `${target}/${role}.webp`;
          outputs.set(path, image);
          if (role === "cover") entry.cover = { path, sha256: hash(image) };
        }
      }
      entries.push(entry);
      const image = entry.cover
        ? `<img src="${entry.cover.path}" width="72" alt="${escape(manifest.name)}">`
        : "—";
      const authorName = escape(manifest.author?.name ?? "未署名");
      const authorUrl = manifest.author?.url;
      const author =
        typeof authorUrl === "string" && /^https?:\/\//.test(authorUrl)
          ? `<a href="${escape(authorUrl)}">${authorName}</a>`
          : authorName;
      rows.push(
        `<tr><td align="center">${image}</td><td><a href="${source}/character.json">${escape(manifest.name)}</a></td><td>${escape(manifest.description ?? "")}</td><td>${author}</td><td><a href="${packagePath}">下载 .limea</a></td></tr>`,
      );
    }
    if (entries.length) {
      if (entries.length > 500) throw new Error("单个作品角色超过 500 张");
      catalog.works.push({ id: work.id, name: work.name, characters: entries });
      tables.push(
        `<tr><td colspan="5">${work.icon ? `<img src="${work.icon.path}" width="28" alt=""> ` : ""}<strong>${escape(work.name)}</strong></td></tr>\n${rows.join("\n")}`,
      );
    }
    const published = `${work.id}/characters`;
    const existing = await filesIn(root, published).catch((error) => {
      if (error.code === "ENOENT") return [];
      throw error;
    });
    if (existing.some((path) => !outputs.has(path)))
      throw new Error("正式目录存在多余文件，请先核对清理");
  }
  for (const directory of await readdir(root, { withFileTypes: true })) {
    if (directory.isDirectory() && !ids.has(directory.name)) {
      if (
        await lstat(join(root, directory.name, "characters_dev"))
          .then(() => true)
          .catch(() => false)
      )
        throw new Error("源码目录的作品没有登记到 works.json");
    }
  }
  if (catalog.works.length > 100)
    throw new Error("商店有角色的作品超过 100 个");
  outputs.set("works.json", json(registry));
  outputs.set("catalog.json", json(catalog));
  const readme = await readFile(join(root, "README.md"), "utf8");
  const begin = "<!-- characters:start -->",
    end = "<!-- characters:end -->";
  const from = readme.indexOf(begin),
    to = readme.indexOf(end);
  if (from < 0 || to < from) throw new Error("首页缺少自动生成区标记");
  outputs.set(
    "README.md",
    Buffer.from(
      readme.slice(0, from + begin.length) +
        "\n\n" +
        "<!-- prettier-ignore -->\n<table>\n<thead><tr><th>立绘</th><th>角色</th><th>角色卡</th><th>作者</th><th>安装</th></tr></thead>\n<tbody>\n" +
        tables.join("\n") +
        "\n</tbody>\n</table>" +
        "\n\n" +
        readme.slice(to),
    ),
  );
  for (const [path, data] of outputs) {
    if (check) {
      const actual = await readFile(join(root, path)).catch(() => null);
      if (!actual?.equals(data))
        throw new Error(`生成文件过期：${path}，请运行 npm run build`);
    } else {
      await mkdir(join(root, path, ".."), { recursive: true });
      await writeFile(join(root, path), data);
    }
  }
  console.log(
    `${check ? "校验" : "构建"}通过：${ids.size} 个作品，${characters.size} 张角色卡`,
  );
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
)
  await buildCharacters(
    fileURLToPath(new URL("../", import.meta.url)),
    process.argv.includes("--check"),
  );
