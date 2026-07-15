# Personal Codex Skills

这是一个用于管理个人 Codex skills 的仓库。

当前仓库只包含少量自用 skill，后续会继续按场景沉淀更多可复用的工作流、构建流程、检查清单和自动化说明。

## 目录结构

```text
.
├── README.md
├── build-vs2019-debug-static-lib/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
└── grill-skill-decisions/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```

每个 skill 通常是一个独立目录，至少包含：

- `SKILL.md`：skill 的名称、描述、触发条件和具体执行流程。
- `agents/openai.yaml`：可选，用于补充展示名称、默认提示词或调用策略。

## 当前包含的 Skills

| Skill | 用途 |
| --- | --- |
| `build-vs2019-debug-static-lib` | 将 C/C++ 项目按固定 Windows Debug package 流程构建为 Visual Studio 2019 v142 x64 Debug `/MTd` 静态库，并生成 C++17 consumer teaching tests。 |
| `grill-skill-decisions` | 在编写 `Codex Skill`、`SKILL.md`、`agents/openai.yaml` 或制定方案前，先通过一问一答澄清场景、触发条件、边界、失败模式、输出物和验证标准。 |

## 使用方式

将本仓库放在 Codex 的 skills 目录下：

```powershell
C:\Users\Administrator\.codex\skills
```

Codex 启动后会从该目录发现可用 skill。需要使用某个 skill 时，可以在提示词中显式引用，例如：

```text
Use $build-vs2019-debug-static-lib to build and package this project.
```

```text
Use $grill-skill-decisions to clarify the scenario before drafting a Codex Skill.
```

也可以通过 skill 的描述关键词触发隐式调用，具体取决于 skill 配置。

## 新增 Skill 约定

新增自用 skill 时，建议按以下方式组织：

```text
skill-name/
├── SKILL.md
└── agents/
    └── openai.yaml
```

建议保持这些约定：

- 目录名使用清晰、稳定的英文短横线命名。
- `SKILL.md` 顶部包含 `name` 和 `description` 元数据。
- 描述中写清楚适用场景、触发关键词和主要约束。
- 把可复用流程、验收清单、注意事项写进 skill，而不是散落在临时提示词里。
- 不提交密钥、账号、私有 token 或只适用于单台机器的敏感配置。

## 维护说明

这个仓库主要用于个人工作流复用，不追求通用插件市场级别的抽象。新增 skill 时优先保证：

- 自己能稳定复用。
- 描述足够明确，避免误触发。
- 操作步骤可验证。
- 输出结果便于检查和交付。

如果本地存在 Codex 内置的 `.system/` skills，它们通常不属于本仓库维护范围，不建议作为个人 skill 一起提交。
