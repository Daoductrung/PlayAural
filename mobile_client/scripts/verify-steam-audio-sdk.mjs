import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, "../..");
const sdkRoot = join(repositoryRoot, "cosmos/steamaudio-sys/phonon");
const manifestPath = join(sdkRoot, "UPSTREAM.json");
const minimumAndroidLoadAlignment = 16 * 1024;
const pinnedSteamAudioVersion = "4.8.1";
const androidArtifacts = Object.freeze({
  "android/arm64-v8a/libphonon.so": Object.freeze({ elfClass: 2, machine: 183 }),
  "android/armeabi-v7a/libphonon.so": Object.freeze({ elfClass: 1, machine: 40 }),
  "android/x86/libphonon.so": Object.freeze({ elfClass: 1, machine: 3 }),
  "android/x86_64/libphonon.so": Object.freeze({ elfClass: 2, machine: 62 }),
});
const requiredArtifacts = Object.freeze([
  "LICENSE.md",
  "THIRDPARTY.md",
  "TRADEMARK_RIGHTS.md",
  ...Object.keys(androidArtifacts),
  "ios/libphonon.a",
  "phonon.dll",
  "phonon.h",
  "phonon.lib",
  "phonon_version.h",
].sort());
const sha256Pattern = /^[a-f0-9]{64}$/;

function sha256(contents) {
  return createHash("sha256").update(contents).digest("hex");
}

function androidLoadAlignments(contents) {
  if (
    contents.length < 64
    || contents[0] !== 0x7f
    || contents.subarray(1, 4).toString("ascii") !== "ELF"
    || contents[5] !== 1
  ) {
    throw new Error("Android Steam Audio artifact is not a little-endian ELF binary");
  }
  const elfClass = contents[4];
  const is64Bit = elfClass === 2;
  if (!is64Bit && elfClass !== 1) {
    throw new Error(`Unsupported ELF class ${elfClass}`);
  }
  const programHeaderOffset = is64Bit
    ? Number(contents.readBigUInt64LE(32))
    : contents.readUInt32LE(28);
  const programHeaderEntrySize = contents.readUInt16LE(is64Bit ? 54 : 42);
  const programHeaderCount = contents.readUInt16LE(is64Bit ? 56 : 44);
  const alignments = [];
  for (let index = 0; index < programHeaderCount; index += 1) {
    const offset = programHeaderOffset + (index * programHeaderEntrySize);
    if (offset < 0 || offset + programHeaderEntrySize > contents.length) {
      throw new Error("ELF program-header table exceeds the artifact size");
    }
    if (contents.readUInt32LE(offset) !== 1) {
      continue;
    }
    alignments.push(is64Bit
      ? Number(contents.readBigUInt64LE(offset + 48))
      : contents.readUInt32LE(offset + 28));
  }
  if (!alignments.length) {
    throw new Error("Android Steam Audio artifact has no loadable ELF segments");
  }
  return {
    alignments,
    elfClass,
    machine: contents.readUInt16LE(18),
  };
}

function verifyIosArm64Archive(contents) {
  if (contents.subarray(0, 8).toString("ascii") !== "!<arch>\n") {
    throw new Error("iOS Steam Audio artifact is not a Unix static archive");
  }
  const machOMagic = "cffaedfe";
  const arm64CpuType = 0x0100000c;
  let arm64Members = 0;
  let offset = 8;
  while (offset + 60 <= contents.length) {
    const header = contents.subarray(offset, offset + 60);
    if (header.subarray(58, 60).toString("ascii") !== "`\n") {
      throw new Error("iOS Steam Audio archive contains an invalid member header");
    }
    const memberSize = Number.parseInt(
      header.subarray(48, 58).toString("ascii").trim(),
      10,
    );
    const memberEnd = offset + 60 + memberSize;
    if (!Number.isSafeInteger(memberSize) || memberSize < 0 || memberEnd > contents.length) {
      throw new Error("iOS Steam Audio archive member exceeds the artifact size");
    }
    const rawName = header.subarray(0, 16).toString("ascii").trim();
    const extendedNameLength = rawName.startsWith("#1/")
      ? Number.parseInt(rawName.slice(3), 10)
      : 0;
    if (
      !Number.isSafeInteger(extendedNameLength)
      || extendedNameLength < 0
      || extendedNameLength > memberSize
    ) {
      throw new Error("iOS Steam Audio archive has an invalid extended member name");
    }
    const payloadOffset = offset + 60 + extendedNameLength;
    if (contents.subarray(payloadOffset, payloadOffset + 4).toString("hex") === machOMagic) {
      if (contents.readUInt32LE(payloadOffset + 4) !== arm64CpuType) {
        throw new Error("iOS Steam Audio archive contains a non-arm64 Mach-O member");
      }
      arm64Members += 1;
    }
    offset = memberEnd + (memberEnd % 2);
  }
  if (offset !== contents.length || arm64Members === 0) {
    throw new Error("iOS Steam Audio archive has no complete arm64 Mach-O members");
  }
}

export async function verifySteamAudioSdk() {
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  if (manifest.version !== pinnedSteamAudioVersion) {
    throw new Error(`Unsupported Steam Audio SDK version ${manifest.version}`);
  }
  const listedArtifacts = Object.keys(manifest.artifacts ?? {}).sort();
  if (
    listedArtifacts.length !== requiredArtifacts.length
    || listedArtifacts.some((path, index) => path !== requiredArtifacts[index])
  ) {
    throw new Error("Steam Audio SDK manifest does not contain the complete pinned artifact set");
  }
  const verified = [];
  for (const [relativePath, expectedDigest] of Object.entries(manifest.artifacts)) {
    if (!sha256Pattern.test(expectedDigest)) {
      throw new Error(`Invalid Steam Audio checksum for ${relativePath}`);
    }
    const artifactPath = resolve(sdkRoot, relativePath);
    if (!artifactPath.startsWith(`${resolve(sdkRoot)}${sep}`)) {
      throw new Error(`Steam Audio artifact escapes the SDK directory: ${relativePath}`);
    }
    const contents = await readFile(artifactPath);
    const actualDigest = sha256(contents);
    if (actualDigest !== expectedDigest) {
      throw new Error(
        `Steam Audio artifact checksum mismatch for ${relativePath}: ${actualDigest}`,
      );
    }
    const expectedAndroidAbi = androidArtifacts[relativePath];
    if (expectedAndroidAbi) {
      const metadata = androidLoadAlignments(contents);
      if (
        metadata.elfClass !== expectedAndroidAbi.elfClass
        || metadata.machine !== expectedAndroidAbi.machine
      ) {
        throw new Error(`Steam Audio artifact ${relativePath} has the wrong Android ABI`);
      }
      const invalidAlignment = metadata.alignments.find(
        (alignment) => alignment < minimumAndroidLoadAlignment,
      );
      if (invalidAlignment !== undefined) {
        throw new Error(
          `Steam Audio artifact ${relativePath} is not 16 KiB page aligned`,
        );
      }
    }
    if (relativePath === "ios/libphonon.a") {
      verifyIosArm64Archive(contents);
    }
    verified.push(relativePath);
  }
  const versionHeader = await readFile(join(sdkRoot, "phonon_version.h"), "utf8");
  for (const [component, value] of [["MAJOR", 4], ["MINOR", 8], ["PATCH", 1]]) {
    if (!new RegExp(`STEAMAUDIO_VERSION_${component}\\s+${value}\\b`).test(versionHeader)) {
      throw new Error(`Steam Audio version header has an unexpected ${component} value`);
    }
  }
  return verified;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const verified = await verifySteamAudioSdk();
  console.log(`Verified Steam Audio SDK artifacts: ${verified.length}`);
}
