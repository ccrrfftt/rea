"""Project-specific checks and assets for this fork's GitHub Releases."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile


def run(*args):
    subprocess.run(args, check=True, env={**os.environ, "HUSKY": "0"})


def version(revision):
    manifest = subprocess.check_output(["git", "show", f"{revision}:package.json"])
    return json.loads(manifest)["version"]


def release_notes(tag):
    if tag != "v" + version("HEAD"):
        raise ValueError("The release notes must match the checked-out version")
    release_version = re.escape(tag[1:])
    entries = Path("CHANGELOG.md").read_text().splitlines()
    start = next(
        (i for i, line in enumerate(entries)
         if re.match(rf"^## \[?{release_version}(?:\]|\s|$)", line)),
        None,
    )
    if start is None:
        raise ValueError(f"No CHANGELOG.md entry for {tag}")
    end = next((i for i in range(start + 1, len(entries)) if entries[i].startswith("## ")), len(entries))
    print("\n".join(entries[start + 1:end]).strip())
    print(f"\nDownload the archive and verify it with `sha256sum -c SHA256SUMS.txt`. "
          f"Install this fork's CLI using `npm install -g ./rea-agents-{tag[1:]}.tgz`. "
          "Run `rea --help` to check the installation. "
          "Node.js compatibility is specified in package.json. Optional analysis providers require separate setup.")


def package(output):
    if sys.platform != "linux":
        raise RuntimeError("The bundled Windows x64 addon requires a Linux build runner")
    if not shutil.which("x86_64-w64-mingw32-g++"):
        run("sudo", "apt-get", "update")
        run("sudo", "apt-get", "install", "--no-install-recommends", "-y", "g++-mingw-w64-x86-64")
    run("npm", "run", "build:windows-native")
    run("npm", "run", "verify:windows-native:artifact")
    run("npm", "run", "verify:package")
    run("npm", "pack", "--silent", "--pack-destination", str(output))
    current = version("HEAD")
    archive = output / f"rea-agents-{current}.tgz"
    with tarfile.open(archive, mode="r:gz") as packed:
        manifest = json.load(packed.extractfile("package/package.json"))
        native = json.load(packed.extractfile("package/native/windows/build/manifest.json"))
        addon = packed.extractfile("package/native/windows/build/rea-windows-x64.node")
        if (manifest["name"] != "rea-agents" or manifest["version"] != current
                or native["packageVersion"] != current
                or native["artifactSha256"] != hashlib.sha256(addon.read()).hexdigest()):
            raise RuntimeError("Packed package or Windows addon differs from the release version")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{digest}  {archive.name}\n")


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    if command == "version":
        print("v" + version(*arguments))
    elif command == "prerelease":
        print("true" if "-" in arguments[0] else "false")
    elif command == "check":
        run("npm", "ci")
        run("npm", "run", "check:fast")
        run("npm", "run", "metadata:check")
        run("npm", "run", "test:focused", "--", "tests/boundary/filesystem/releaseWorkflow.test.ts")
    elif command == "notes":
        release_notes(*arguments)
    elif command == "package":
        package(Path(arguments[0]).resolve(strict=True))
    else:
        sys.exit(f"Unknown command: {command}")
