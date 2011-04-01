CREATE TABLE IF NOT EXISTS "packages" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "category" TEXT NOT NULL,
    "package" TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS "packages_catpkg" ON packages (category, package);

CREATE TABLE IF NOT EXISTS "herds" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "herd" TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS "herds_herd" ON herds (herd);

CREATE TABLE IF NOT EXISTS "maintainers" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "maintainer" TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS "maintainers_maintainer" ON maintainers (maintainer);

CREATE TABLE IF NOT EXISTS "package_herds" (
    "herd_id" INTEGER NOT NULL,
    "package_id" INTEGER NOT NULL,
    PRIMARY KEY("herd_id", "package_id")
);

CREATE TABLE IF NOT EXISTS "package_maintainers" (
    "maintainer_id" INTEGER NOT NULL,
    "package_id" INTEGER NOT NULL,
    PRIMARY KEY("maintainer_id", "package_id")
);

CREATE TABLE IF NOT EXISTS "versions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "package_id" INTEGER NOT NULL,
    "slot" TEXT NOT NULL,
    "revision" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "packaged" INTEGER NOT NULL DEFAULT (0)
);

CREATE INDEX IF NOT EXISTS "versions_packaged" on versions (package_id, packaged);
CREATE UNIQUE INDEX IF NOT EXISTS "versions_version" on versions (package_id, version, slot, revision);

CREATE TABLE IF NOT EXISTS "upstream_urls" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version_id" INTEGER NOT NULL,
    "url" TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS "upstream_version" on upstream_urls (version_id);
CREATE UNIQUE INDEX IF NOT EXISTS "upstream_unique_urls" on upstream_urls (version_id, url);