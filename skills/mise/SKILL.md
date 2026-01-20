---
name: mise
description: mise cli 適合需要頻繁切換工具版本與多語言環境的情境。它可以選擇將工具版本、環境變數與任務定義集中於單一設定檔，進入目錄即可自動生效，並在執行任務時套用正確的版本與設定，減少手動操作與環境不一致問題，提升整體開發體驗。
---

# Mise Skill

Mise is a comprehensive tool for managing development environments. It handles tool version management, environment variable configuration, and task execution, replacing multiple single-purpose tools with a unified experience.

## Getting Started

Based on [Getting Started](references/getting_started.md).

Mise allows you to run tools without installing them globally or recursively.

### Core Concepts

- **Exec (`mise x`)**: Run a tool in an ephemeral environment.
  ```bash
  mise exec node@20 -- node app.js
  ```
- **Use (`mise use`)**: Install and pin a tool version for the current directory.
  ```bash
  mise use node@20
  ```
- **Run (`mise run`)**: Execute tasks defined in `mise.toml`.
- **Activate**: Integrate mise with your shell to automatically load tools and env vars when entering directories.

### Common Commands

- `mise ls`: List installed tools.
- `mise install`: Install tools defined in config.
- `mise doctor`: Diagnose issues.
- `mise upgrade`: Upgrade tool versions.

## Environments

Based on [Environments](references/environments.md).

Mise manages environment variables via `mise.toml` or `[env]` sections.

### Features

- **Project Structure**: Define env vars per project in `mise.toml`.
- **Dynamic Values**: Use templates like `{{config_root}}` or `{{env.HOME}}`.
- **Secrets**: Encrypt sensitive variables using `mise set --age-encrypt`.
- **Loading from Files**: Load `.env` files using `env._.file`.
  ```toml
  [env]
  _.file = ".env"
  NODE_ENV = "production"
  ```
- **Redaction**: Mark variables as sensitive to prevent leakage in logs.

## Dev Tools

Based on [Dev Tools](references/dev_tools.md).

Mise is a polyglot tool version manager, supporting hundreds of languages and tools via a registry and plugins.

### Key Capabilities

- **Backends**: Supports multiple backends (core, asdf, cargo, npm, go, etc.).
- **Shims**: Use shims for IDE integration or non-interactive shells.
- **Lockfiles**: Use `mise.lock` for reproducible tool versions across teams (Experimental).
- **Tool Stubs**: Generate executable stubs for tools to avoid full installation overhead until needed.

### Configuration

Tools are defined in the `[tools]` section of `mise.toml`:

```toml
[tools]
node = "20"
python = "3.11"
terraform = "1.5"
```

## Tasks

Based on [Tasks](references/tasks.md).

Mise includes a task runner similar to `make` or `npm scripts` but language-agnostic.

### Task Definitions

Tasks can be defined in `mise.toml` or as standalone scripts in `mise-tasks/`.

```toml
[tasks.build]
description = "Build the project"
run = "cargo build"
depends = ["lint"]
sources = ["src/**/*.rs"]
outputs = ["target/debug/app"]
```

### Features

- **Dependencies**: Define task execution order (`depends`, `depends_post`).
- **Parallelism**: Runs independent tasks in parallel.
- **Caching**: Skip tasks if sources haven't changed.
- **Watch**: Re-run tasks on file changes (`mise watch`).
- **Arguments**: Pass arguments to tasks using the usage spec.

## Other Reference Materials

For more detailed information, refer to the detailed markdown files in the `references/` directory:

- [advanced.md](references/advanced.md): Advanced configuration, cookbooks for specific languages, and shell integration tips.
- [cli.md](references/cli.md): Complete reference for all CLI commands and flags. **Try `mise [COMMAND] -h` first before consulting this reference.**
- [plugins.md](references/plugins.md): Guide to using and creating plugins (compatible with asdf).
- [other.md](references/other.md): Miscellaneous documentation and FAQs.
- [index.md](references/index.md): Documentation index.
