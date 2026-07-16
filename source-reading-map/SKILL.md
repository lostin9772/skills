---
name: source-reading-map
description: Use only when the user explicitly invokes $source-reading-map, source-reading-map, "源码阅读地图", "源码总览文档", or asks to generate a source-reading .mhtml / PROJECT_SOURCE_ANALYSIS.md / detailed Chinese source comments for a large C/C++ project, especially Windows reverse-engineering, security, hook, runtime, or instrumentation codebases. Do not use for ordinary local code-snippet explanation unless explicitly requested.
---

# Source Reading Map

## 核心目标

把大型 C/C++ 源码项目整理成可阅读、可持续推进的源码阅读体系，默认面向 Windows 逆向、安全、hook、instrumentation、runtime、loader、patching、thread、memory、exception、symbol 等底层项目。

默认交付三类结果：

1. `source-reading-map.mhtml`：放在源码项目根目录，作为单文件离线总览地图，包含阅读阶段、核心文件、调用链、模块关系和丰富图示。
2. `PROJECT_SOURCE_ANALYSIS.md`：放在源码项目根目录，作为长期维护的详细中文分析主文档。
3. 源码中文注释：直接写入阅读路线中的核心源码文件，服务于后续逐文件阅读。

## 触发与边界

- 只在用户显式要求使用 `$source-reading-map`、`source-reading-map`、"源码阅读地图"、"源码总览文档"、"生成源码阅读 .mhtml" 等任务时使用。
- 不要在用户只是粘贴一段代码并询问局部含义时自动使用。
- 默认不编译、不运行目标项目、不联网、不安装依赖。
- 可以读取源码、README、构建文件、示例、测试和本地文档。
- 可以运行只读分析命令，例如 `rg`、`git ls-files`、`Get-ChildItem`、`git status --short`、文件统计脚本。
- 可以修改源码，但只添加服务阅读的中文注释，不主动修改代码行为、控制流、API、格式化风格或构建配置。
- 如果项目根目录不明确，先用一个问题向用户确认。

## 默认工作流

### 1. 扫描项目证据

先收集证据，再判断阅读路线。不要只凭文件名或目录名猜核心模块。

优先查看：

- `README*`、`docs/`、`doc/`、`manual/`、`wiki/`、设计说明。
- 构建入口：`CMakeLists.txt`、`*.sln`、`*.vcxproj`、`Makefile`、`meson.build`、`BUILD`、`WORKSPACE`、`premake*.lua`。
- 目录结构和文件数量，区分项目自身源码、`third_party/`、`vendor/`、`externals/`、`deps/`、generated code、examples、tests。
- public headers、exported API、核心 class/struct、全局初始化对象。
- examples/tests 中展示的入口用法。
- 符号搜索结果。

常用搜索方向：

- 入口：`main`、`wmain`、`DllMain`、`DriverEntry`、`EfiMain`、`Init`、`Initialize`、`Start`、`Load`、`Attach`。
- 生命周期：`Create`、`Install`、`Enable`、`Disable`、`Remove`、`Detach`、`Cleanup`、`Shutdown`、`Unload`。
- 逆向/底层机制：`Hook`、`Patch`、`Trampoline`、`Detour`、`Injector`、`Thread`、`Memory`、`Exception`、`VEH`、`SEH`、`Symbol`、`Disassemble`、`Instruction`、`VTable`。

### 2. 生成阅读路线

按阅读阶段组织，不按目录机械铺开。每个阶段至少说明：

- 这一阶段要解决的阅读问题。
- 应先看的文件和符号。
- 关键调用链或数据结构。
- 可以暂时跳过的目录或文件。
- 本阶段和下一阶段的连接点。

默认阶段：

1. 项目入口和最小用法。
2. public API 与核心抽象。
3. 初始化、安装、启用、禁用、清理等主流程。
4. 底层机制，例如 hook/patch、thread、memory、exception、symbol、instruction relocation。
5. examples/tests 如何反向说明真实用法。
6. 后续逐文件重注释路线。

### 3. 生成 `source-reading-map.mhtml`

在源码项目根目录生成 `source-reading-map.mhtml`。它是快速进入项目的单文件离线地图，不是详细正文的替代品。

内容应包含：

- 项目一句话定位。
- 阅读阶段路线图。
- 核心目录和模块职责。
- 核心文件清单和阅读优先级。
- public API 到实现文件的映射。
- 关键调用链和生命周期。
- 关键机制索引。
- 暂时跳过清单：第三方依赖、generated code、重复样板、低价值文件。
- 连续源码注释批次计划。

图示要求：

- 优先包含架构图、阶段路线图、模块依赖图、初始化/安装/清理流程图、关键调用链图、核心数据结构关系图。
- 使用 HTML/CSS、内联 SVG 或静态图示，避免依赖外部 JS/CSS/图片。
- 如果先生成 HTML，再用 `scripts/pack_mhtml.py` 打包成 `.mhtml`。
- 最终 `.mhtml` 必须能作为单文件复制和离线打开。

### 4. 生成 `PROJECT_SOURCE_ANALYSIS.md`

在源码项目根目录生成 `PROJECT_SOURCE_ANALYSIS.md`。这是详细中文分析主文档，便于后续版本管理、搜索、修改和继续扩写。

建议结构：

```markdown
# PROJECT_SOURCE_ANALYSIS

## 项目定位
## 证据来源
## 顶层目录地图
## 阅读路线
## 核心模块详解
## public API 与实现映射
## 初始化与生命周期
## 关键调用链
## 关键数据结构
## 逆向/底层机制专题
## examples/tests 阅读价值
## 第三方依赖边界
## 核心文件注释计划
## 已完成注释批次
## 未决问题和下一步
```

详细文档要比 `.mhtml` 更展开，可以记录更多背景知识、机制解释、证据引用、推断依据和未确认点。

### 5. 分批添加源码中文注释

大项目默认分阶段推进。第一阶段交付 `.mhtml`、`.md` 初版和核心文件清单；然后按阅读阶段逐批给核心文件添加中文注释。

源码注释阶段默认连续推进，不要每批结束后等待用户再次输入"继续"。每批完成后简短汇报进度并立刻进入下一批，直到阅读路线中的核心文件注释完成、用户明确要求暂停/停止，或遇到真实阻塞。

每批完成后记录并汇报：

- 已注释文件。
- 每个文件的注释重点。
- 新确认的调用链或模块关系。
- 下一批将自动处理的文件。

只有在以下情况才停止自动连续注释：

- 用户明确要求暂停、停止或改变注释范围。
- 项目根目录、核心文件范围或写入权限不明确。
- 单批文件过大导致上下文不足，需要重新切分批次。
- 发现继续注释会修改代码行为、破坏原始注释结构或越过已确认的第三方/generated code 边界。
- 已完成阅读路线中所有核心文件的详细中文注释。

## 源码注释规则

默认使用普通中文注释，不加 `[READING-NOTE]` 等统一标记。因为用户主要阅读英文项目，中文注释本身足以区分新增阅读注释。

注释可以尽可能详细，不以精简为目标。遇到难理解的机制，可以扩展背景知识、逆向语境、Windows 内核/用户态差异、hook/patch 原理、ABI/调用约定、线程安全、异常处理、指令级细节和跨模块影响。

优先注释：

- 文件级职责：放在 license、版权头、generated notice 之后，不插入这些原始头部中间。
- 核心 class/struct/enum：说明抽象边界、对象生命周期、关键字段。
- public API：说明调用者视角、参数含义、返回值、失败条件、与实现文件的连接。
- 关键函数：在函数定义前或函数体开头说明它解决的问题、前置条件、调用链位置。
- 复杂流程块：在关键分支、循环、状态转换、错误处理、资源释放前解释为什么这样写。
- 跨模块调用点：说明调用到哪里、为什么跨过去、返回后依赖什么状态。
- 逆向关键点：hook 安装、代码修改、线程暂停、内存保护、异常分发、符号解析、指令解码、trampoline、relocation 等。

不要这样做：

- 不要夹断原作者英文注释、Doxygen/Javadoc 注释、license、版权头或 generated code 说明。
- 不要把英文注释直接替换成中文。
- 不要为了注释而改变代码行为、宏条件、include 顺序、格式化体系或构建脚本。
- 不要重注释第三方依赖、vendor code、generated code；只在文档中说明它们的边界和用途。
- 不要对 getter/setter、重复样板、显而易见的一行包装函数强行写长注释，除非它们在阅读路线中承担关键抽象意义。

已有英文注释时：

- 保留英文注释完整性。
- 在英文注释后方、函数体前或关键代码块前追加中文解释。
- 如果英文注释已经解释了表层含义，中文注释应补充阅读路线、调用链、设计意图、底层机制或容易误读的点。

## 第三方、示例和测试

- `third_party/`、`vendor/`、`externals/`、`deps/` 默认只做边界说明，不重注释。
- examples/tests 是理解入口和用法的重要证据，要认真分析。
- 重注释优先项目自身核心实现；examples/tests 只有在它们是最清晰入口或项目本身核心样例时才加入注释批次。

## MHTML 打包脚本

使用 `scripts/pack_mhtml.py` 把已生成的 HTML 打包为 `.mhtml`：

```powershell
python scripts/pack_mhtml.py source-reading-map.html source-reading-map.mhtml
```

脚本只负责打包，不负责项目分析。项目理解、图示内容、HTML 结构、Markdown 文档和源码注释都由 agent 根据当前项目证据生成。

## 验证与汇报

完成后至少检查：

- `source-reading-map.mhtml` 是否在项目根目录。
- `PROJECT_SOURCE_ANALYSIS.md` 是否在项目根目录。
- `.mhtml` 是否是 `multipart/related` 单文件。
- 已注释文件是否只增加中文阅读注释，没有修改代码逻辑。
- 是否保留原英文注释、license、Doxygen 和 generated notice 的完整性。
- 是否明确说明没有编译、没有运行目标项目，除非用户另行要求。

如果只能完成部分阶段，要明确说明已完成内容、未完成内容和下一步建议。
