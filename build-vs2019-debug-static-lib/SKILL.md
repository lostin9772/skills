---
name: build-vs2019-debug-static-lib
description: "用于把当前 C/C++ 项目按固定 Windows Debug package 流程构建为 Visual Studio 2019 v142 x64 Debug /MTd static .lib，导出 include/lib/.pdb，并创建 C++17 consumer teaching tests；触发关键词包括 VS2019, Visual Studio 16 2019, CMake + Ninja, Debug static lib, /MTd, /Zi, C++17 public headers, package, teaching test suite, high-risk functional tests。"
---

# VS2019 Debug 静态库打包流程

## 目标

将当前项目交付为可被消费端直接引用的 Debug 静态库包，并证明它能在 VS2019 + C++17 消费项目中源码级调试：

- `package/include/`：公开 `.h/.hpp`，保留相对路径。
- `package/lib/`：生成的 Debug static `.lib`。
- `package/lib/`：与 `.lib` 放在一起的 compiler `.pdb`。
- 独立消费端教学测试项目：位于 `package` 外，只通过相对路径引用 `package/include` 和 `package/lib`。

## 固定工具链

严格使用并核对以下环境；如果本机不匹配，不要静默替换为更新版本：

- VS: `Visual Studio 2019 Professional 16.11.57`
- Toolset: `v142`
- MSVC: `14.29.30133`
- Compiler: `cl 19.29.30159.0`
- Windows SDK: `10.0.19041.0`
- Arch: `x64`
- Config: `Debug`
- Runtime: `/MTd`
- Output: static `.lib`
- Build system: `CMake + Ninja`

优先从 `VS2019 Developer PowerShell`、`vcvars64.bat`、`vswhere`、`cl /Bv`、`cmake --version`、`ninja --version` 核对环境。版本不符时先报告差异和影响，再决定是否继续。

## 构建约束

配置第三方库本体时遵守这些硬约束：

- 使用 `CMake + Ninja` 构建第三方库本体，不用 Visual Studio `.sln` 构建库本体。
- 生成可源码级调试的 Debug static `.lib`。
- 使用 Debug CRT 静态运行库 `/MTd`，不要落到 `/MDd`。
- 使用 `Program Database (/Zi)`，保留 compiler PDB。
- 禁止优化：使用 `/Od` 和 `/Ob0`。
- 不要使用 `/O2`、`/Ob2`、`/GL`；除明确关闭功能级链接的 `/Gy-` 外，不引入会影响源码级调试的优化配置。
- 不要定义 `NDEBUG`；应定义 `_DEBUG`。
- 使用 `Unicode` 字符集，确保定义 `UNICODE` 和 `_UNICODE`。
- Debug 产物应允许消费端断点进入第三方库源码，或进入已正确映射的源码路径。

推荐的 CMake 配置方向：

```powershell
cmake -S <source> -B <build-debug> -G Ninja `
  -DCMAKE_BUILD_TYPE=Debug `
  -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDebug `
  -DCMAKE_C_FLAGS_DEBUG="/Od /Ob0 /Zi /MTd" `
  -DCMAKE_CXX_FLAGS_DEBUG="/Od /Ob0 /Zi /MTd" `
  -DCMAKE_COMPILE_PDB_OUTPUT_DIRECTORY=<package-or-build-pdb-dir>
cmake --build <build-debug> --config Debug
```

如果项目已有自己的 CMake 选项、install 规则或 runtime 设置，优先沿用项目方式；只做为满足上述 Debug 调试约束所必需的最小改动。

## C++ 标准策略

分开处理“库本体编译标准”和“公开头文件消费标准”：

- 编译第三方库本体时，使用第三方库或 CMake 项目默认的 C++ 标准配置。
- 不要为了统一消费端标准而强制把第三方库源码改成 `/std:c++17`。
- 不要降低第三方库内部实现需要的 C++ 标准。
- 导出的 public `.h/.hpp` 必须能被 `/std:c++17` 消费项目正常包含和编译。

检查 `include/` 中所有公开头文件。若 public API 暴露 C++20/C++23/C++26 或更新标准专属特性，例如 `concepts`、`requires`、`consteval`、`constinit`、`char8_t`、`std::format`、`std::span`、`std::ranges`、`std::source_location`、`std::expected`、`std::print`、`std::mdspan`，优先在公开头文件或 API 兼容层中替换、包装或降级为 C++17 可编译形式。避免无必要改动第三方库内部实现。

## 打包步骤

1. 先阅读 `README`、`CMakeLists.txt`、`docs`、`examples`、`include` 和导出目标，识别库名、公开头文件、主要 API、构建选项和依赖。
2. 用固定工具链配置 Debug Ninja build，确保 `/MTd`、`/Zi`、`/Od`、`/Ob0`、`_DEBUG`、`UNICODE`、`_UNICODE` 生效。
3. 构建 static `.lib`，保留对应 compiler `.pdb`。
4. 生成 import-ready Debug package：
   - `.lib` 放入 `package/lib/`。
   - `.pdb` 放在对应 `.lib` 旁边。
   - required public `.h/.hpp` 复制到 `package/include/`，保留相对路径。
5. 检查实际编译命令、`compile_commands.json`、Ninja 输出或生成文件，确认没有 `NDEBUG`、`/O2`、`/Ob2`、`/GL`、错误 runtime 或缺失 PDB。

## 消费端教学测试项目

在 `package` 外创建独立测试项目目录，用于验证打包结果，而不是引用源码目录或 build tree：

- 生成 Visual Studio 2019 可直接打开且可搬迁的 `.sln`。
- `.sln/.vcxproj` 使用 `Visual Studio 16 2019`、`x64`、`v142`、`Debug`、`/MTd`、`Unicode`、`/std:c++17`。
- `.vcxproj` 只通过相对路径引用 `package/include` 和 `package/lib`。
- 不允许引用源码目录中的 headers、sources 或 build tree。
- 同时提供 `CMakeLists.txt`，用于命令行验证 `cmake --build --config Debug`。
- 交付给用户直接打开的 `.sln/.vcxproj` 必须可搬迁，不能依赖 CMake build tree 中的绝对路径。

测试内容应根据 `README`、`Examples`、`docs` 和 public headers 识别主要功能点，编写可运行的教学案例：

- 覆盖公开 API 的主要功能和典型使用路径。
- 每个测试案例包含清晰中文注释，说明演示的 API、预期行为和验证点。
- 测试运行时用中文打印分步骤结果。
- 在 VS2019 中打开 `.sln` 后 `Build Solution` 必须成功。
- 命令行 CMake 验证也应能构建成功。
- 如果消费端因公开头文件不兼容 C++17 失败，继续适配 public headers，直到 C++17 消费端验证通过。
- 若消费端教学测试包含中文输出，必须使用 UTF-8 源文件与 /utf-8 编译选项，并在程序入口处设置 Windows 控制台输入/输出代码页为 CP_UTF8，不得依赖用户手动执行 chcp 65001。

## 高风险功能测试

遇到系统 API、进程内 patch、hook、内存保护修改、异常/断点、线程/同步、文件/网络/注册表/系统资源等高风险能力时，不要自动降级为“只编译示例”。优先编写可运行、可重复、影响可控的功能测试。

只有在会导致测试进程不可恢复崩溃、破坏系统状态、需要外部敏感环境，或当前平台确实不支持时，才允许改为只编译示例。此时必须在中文注释和中文运行输出中说明原因。

高风险测试必须做到：

- 尽量选择当前测试进程内、行为稳定、可重复、清理明确的目标。
- 中文注释说明测试目标、触发方式、预期行为、验证点、潜在风险和清理/恢复逻辑。
- 中文运行输出覆盖准备、执行、验证、清理和恢复验证。
- 测试完成后恢复原状态；无法完全自动恢复时，明确说明剩余影响和人工恢复方式。

## 验收清单

完成前逐项确认：

- 固定工具链和版本已核对；任何偏差已明确记录。
- 第三方库本体由 `CMake + Ninja` 生成 Debug static `.lib`。
- `.lib` 使用 `/MTd`、`/Zi`、`/Od`、`/Ob0`，定义 `_DEBUG`、`UNICODE`、`_UNICODE`，未定义 `NDEBUG`。
- compiler `.pdb` 已生成并放在 `package/lib/` 中对应 `.lib` 旁边。
- public headers 已复制到 `package/include/` 并能被 `/std:c++17` 消费项目编译。
- 消费端测试项目位于 `package` 外，且只通过相对路径引用 package。
- VS2019 `.sln` 可直接打开并 `Build Solution` 成功。
- 消费端 `CMakeLists.txt` 可通过 `cmake --build --config Debug` 验证。
- 功能测试运行成功；高风险测试有中文步骤输出和清理/恢复验证。

最终回复用户时，给出 package 路径、`.lib`/`.pdb` 路径、消费端测试项目路径、执行过的关键命令、验证结果，以及任何无法满足的工具链或平台限制。
