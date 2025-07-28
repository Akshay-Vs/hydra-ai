module.exports = {
  extends: ["@commitlint/config-conventional"],
  parserPreset: {
    parserOpts: {
      headerPattern:
        /^(\p{Emoji_Presentation}\s*)?(\w+)(\(([\w\-_,\s]+)\))?!?: (.+)$/u,
      headerCorrespondence: [
        "emoji",
        "type",
        "scopeWithParens",
        "scope",
        "subject",
      ],
    },
  },
  rules: {
    "subject-empty": [2, "never"],
    "type-empty": [2, "never"],
    // Optional: skip scope validation if you want
    "scope-empty": [0],
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
        "init",
        "release",
        "wip",
        "merge",
      ],
    ],
  },
};
