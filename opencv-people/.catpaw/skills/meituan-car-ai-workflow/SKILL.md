---
name: meituan-car-ai-workflow
description: 美团车机需求研发全流程编排器。统一收集流程所需信息（只需一个学城目录），全流程结束后创建AI工作流总览文档（含阶段跟踪表和用户问题记录），按需路由到需求分析→技术评审→开发三个阶段，并将公共参数传递给各阶段 skill，避免重复询问。触发词：帮我做个需求、开始做需求、我有个新需求、全流程开发、全流程、开始研发、走一遍流程、研发流程。不用于：已明确单阶段操作（单独激活对应 skill 即可）。

metadata:
  skillhub.creator: "shujingwei"
  skillhub.updater: "shujingwei"
  skillhub.version: "V11"
  skillhub.source: "FRIDAY Skillhub"
  skillhub.skill_id: "47793"
  skillhub.high_sensitive: "false"
---

## [MANDATORY] SKILLHUB_METRIC_REPORTER_START
执行本 Skill 的任何操作之前，必须先执行 Skill：`skill-metric-reporter`。
按照 `skill-metric-reporter` 的要求完成 `skill_start` 上报后，再去继续本 Skill 正文。
如果 `skill-metric-reporter` 不可用或执行失败，跳过上报，继续执行本 Skill 正文——不得因上报失败而阻塞审阅流程。
本 Skill 全部操作完成后，同样按照 `skill-metric-reporter` 的要求完成 `skill_end` 上报。
## [MANDATORY] SKILLHUB_METRIC_REPORTER_END

# IRON LAW

1. **上下文节约原则**：主 Agent 永远只读 SubAgent 的 Summary（≤200字），需要详情时才按需 `read_file` memory 快照。SubAgent 的 PENDING 内容用户可直接看到，**主 Agent 不得将 PENDING 内容再次转发给用户**。
   > ⛔ **AP-17 强制自检（每次向用户输出前必做）**：主 Agent 在准备任何输出前，必须先问自己「我即将输出的内容，是否包含 SubAgent 已经输出过的 PENDING 片段（包括文档全文、列表、标题等任何片段）？」若是，立即停止，改为仅等待用户反馈后 resume SubAgent。以「帮助用户理解」、「格式整理」、「摘要展示」等为由重复输出 PENDING 内容，均视为违反本条。
2. **SubAgent 执行原则（O-W 模式）**：每个阶段（Phase 1/2/3）必须通过 `task` 工具启动 SubAgent（即 Worker）执行，主 Agent（即 Orchestrator）不直接调用子 skill 的具体操作。主 Agent 的唯一职责是**调度、决策、通信**，所有阶段执行工作 100% 交由 SubAgent 完成。
3. **人工确认门控**：每个阶段 SubAgent 完成后，主 Agent 向用户展示 Summary 并等待明确确认，**未确认绝不推进下一阶段**。
4. **交叉验证下沉**：SubAgent 内部的交叉校验由其自行创建 Sub-SubAgent 完成，主 Agent 只关注最终产出。
5. **Init 门控**：学城目录和需求信息必须在 Init 阶段一次性收集，Init 确认前不启动任何 SubAgent。
6. 环境初始化/更新操作只在用户主动触发时执行，不在研发流程中自动运行。
7. **Memory 写入原则**：主 Agent 在 Init 确认后立即创建初始 memory 快照，每阶段 SubAgent 完成后更新快照；主 Agent 优先读 SubAgent Summary，**只在 Summary 信息不足时才读取 memory 快照**，避免不必要的文件读取污染上下文。

---

# 美团车机需求研发全流程（Orchestrator-Worker 编排版）

**架构**：主 Agent（Orchestrator：流程编排 + 确认节点 + memory 管理）→ SubAgent（Worker：阶段执行）→ Sub-SubAgent（交叉验证）

```
主 Agent（Orchestrator）
├── Init：收集参数 → 写初始 memory 快照
├── [task] Phase-1 SubAgent（Worker）→ 产出 Summary
│       └── [task] Phase-1 校验 Sub-SubAgent（内部交叉验证）
├── 主 Agent 读 Summary → 更新 memory → 展示给用户 → 等待确认
├── [task] Phase-2 SubAgent（Worker）→ 产出 Summary
│       └── [task] Phase-2 校验 Sub-SubAgent（内部交叉验证）
├── 主 Agent 读 Summary → 更新 memory → 展示给用户 → 等待确认
├── [task] Phase-3 SubAgent（Worker）→ 产出 Summary
│       └── [task] Phase-3 校验 Sub-SubAgent（内部交叉验证）
├── 主 Agent 读 Summary → 更新 memory → 展示给用户 → 等待确认
└── [task] Phase-4 SubAgent（Worker）→ 产出 Summary（知识库同步）
```

## Orchestrator-Worker 核心原则

> 本节提炼自 `ai-workflow` skill 的 Orchestrator-Worker 模式，是主 Agent 行为的基础约束。

**主 Agent（Orchestrator）允许做的事**（完整列表，超出即违规）：
- 分析用户目标，输出阶段任务列表
- 读取 SubAgent（Worker）返回的 Summary（≤200字）
- 决策下一步启动哪个 SubAgent
- 向用户汇报进展或提问
- **写/更新 memory 快照**（纯文本写入 `.catpaw/memory/`）

**主 Agent（Orchestrator）禁止做的事**：
- 直接执行各阶段 skill 的具体操作（读代码文件、调工具、写学城文档）
- 在自己的 context 里累积 SubAgent 的执行细节或代码片段
- 用"顺手"的方式代替 SubAgent 完成实现工作
- **未经必要就读取 memory 快照**（Summary 已足够时不必读文件）

**SubAgent（Worker）的工作模式**：
- 运行在独立 context，对话历史对其不可见
- 通过 `task.prompt` 中注入的自包含上下文执行任务
- 完成后以结构化 Summary 格式返回结果
- 内部可创建 Sub-SubAgent 做交叉验证

---

## 开发环境管理（主动触发）

> **触发条件**：用户明确提出「初始化开发环境」、「更新开发环境」、「安装 skill 依赖」、「更新 skill」等描述时执行。
> **不在研发流程中自动运行**，需用户主动触发。

### A. 流程专属 skill

| Skill | Friday skill_id | 用途 |
|-------|-----------------|------|
| `meituan-car-ai-workflow`（自身） | 47793 | 本 workflow |
| `car-requirement-analysis` | *(读本地 frontmatter)* | 需求分析阶段 |
| `car-tech-review` | *(读本地 frontmatter)* | 技术评审阶段 |
| `car-development-guide` | *(读本地 frontmatter)* | 开发阶段 |

**处理规则**（流程专属 skill）：

| 结果 | 处理方式 |
|------|----------|
| 均为最新版 | 静默跳过 |
| 子 skill **未安装** | `mtskills i <skill名称> -g` 安装最新版，告知用户已安装哪些 |
| 子 skill 有更新 | `mtskills pull <skill名称>` 覆盖本地，告知用户已更新哪些 |
| **自身有更新** | `mtskills pull meituan-car-ai-workflow` 覆盖本地，告知「workflow 已更新，请重新激活」，**⛔ 停止当前操作** |

> ⚠️ 自身更新后必须停止——新版 SKILL.md 尚未加载，继续执行会使用旧逻辑。

### B. 通用工具 skill

| Skill 名称 | 用途 |
|-----------|------|
| `citadel` | 读写学城文档 |
| `ee-ones` | 查询/创建 ONES 工作项 |
| `ee-hpx` | HPX 组件查询与构建 |
| `infra-raptor` | Crash/性能指标查询 |
| `infra-publish` | Horn 配置发布与查询 |
| `infra-logan` | Logan 日志拉取 |

### C. `mtskills` 不可用时

```bash
npm install -g @mtfe/mtskills --registry=http://r.npm.sankuai.com 2>/dev/null
```

- 安装成功 → 用 `mtskills` 重新执行 A/B 节检查
- 安装失败 → 提示用户手动执行 `mtskills pull --all`

---

## Pre-Init：知识库建设检查（必做，先于 Init）

> **目的**：在进入研发流程前，确认项目知识库三件套（AGENTS.md / docs 学城目录 / .mrules）已就绪，避免因缺少上下文导致 AI 输出质量下降。

### 检查项

在工作区根目录执行以下检查：

```bash
# 1. 检查 AGENTS.md
ls AGENTS.md 2>/dev/null && echo "✅ AGENTS.md 存在" || echo "❌ AGENTS.md 缺失"

# 2. 检查 .mrules
ls .mrules 2>/dev/null && echo "✅ .mrules 存在" || echo "❌ .mrules 缺失"
```

对于 docs 学城知识库目录，向用户询问是否已有对应的学城知识库目录链接。

### 检查结果处理

**情况 A：三项均已就绪**

> 静默通过，直接进入 Init 阶段。

**情况 B：存在缺失项（任意一项或多项缺失）**

输出以下提示并**暂停**，等待用户决策：

```
⚠️ 知识库建设检查未通过

以下知识库资产缺失，AI 在需求分析/技术评审/开发阶段将无法获取足够的项目上下文：

[列出缺失项，每项说明用途]
  ❌ AGENTS.md      → 项目编码规范、架构说明、AI 编码约束（R1~R5）
  ❌ .mrules        → AI 规则文件，补充 AGENTS.md 的细粒度约束
  ❌ docs 学城目录   → 需求/技术评审/开发产出文档的存放目录

📚 建议先执行知识库建设，再启动研发流程。

请问你希望如何继续？
  A. 先去建设知识库（推荐）——请在完成后重新激活本 workflow
  B. 跳过知识库检查，直接继续研发流程（知晓风险）
  C. 部分缺失可接受，继续流程（请说明哪些项可忽略）
```

**等待用户明确选择 A / B / C 后再继续**：
- 选 A → 停止，不进入 Init，提示用户完成知识库建设后重新激活
- 选 B → 记录「已知晓知识库缺失风险，用户主动跳过」，进入 Init 阶段
- 选 C → 用户指定可忽略项后，记录豁免原因，进入 Init 阶段

> ⛔ **禁止**：在知识库缺失且未经用户明确选择 B/C 的情况下自动继续研发流程（AP-22）。

---

## Init：初始化问卷（必做）

进入 workflow 后，**一次性**向用户收集：

```
👋 欢迎使用美团车机需求研发全流程

请提供以下信息：

1️⃣  需求信息
    支持：文字描述 / 学城文档链接（自动读取）/ 会议纪要文本

2️⃣  学城文档目录（citadel_parent_id）
    所有产出文档均写入该目录。请提供链接或数字 ID。
    （必填，不可跳过）

3️⃣  从哪个阶段开始？（必填，请明确选择）
    A. 需求分析 → 技术评审 → 开发
    B. 技术评审 → 开发（已有需求分析结论）
    C. 仅开发（已有技术评审结论）
```

**解析规则**：
- 需求信息含学城链接 → `oa-skills citadel getMarkdown --contentId <id>` 读取，展示摘要确认
- `citadel_parent_id` 未提供 → **必须追问**
- 3️⃣ 未回答 → **必须追问，不得自行默认**，用户明确选择 A/B/C 后才可继续

收到完整信息后，向用户展示确认卡：

```
📋 流程初始化确认

需求概要：[AI 提取的 2-3 句摘要]
学城目录：https://km.sankuai.com/collabpage/[citadel_parent_id]
起始阶段：[A/B/C]

确认后将：
  1. 启动研发流程
  2. 全流程完成后在该目录下创建「[需求名称] AI工作流总览」文档
     （包含各阶段产出链接和用户问题记录）

有需要调整的请告知。
```

等待用户明确批准词后：
1. 初始化 memory 快照（见「Memory 管理」章节）
2. 直接进入对应起始阶段（不创建总览文档）

---

## Memory 管理（主 Agent 持久化记忆）

> 主 Agent（Orchestrator）通过写入本地文件实现跨阶段的持久化记忆，保证上下文精简的同时不丢失关键信息。

### 快照文件路径

```bash
{项目根}/.catpaw/memory/car-workflow-<需求slug>-snapshot.md
```

> `需求slug` = 需求名称的短横线小写，如 `搜索POI优化` → `search-poi-opt`

### 初始化（Init 确认后立即执行）

```bash
# 确保目录存在
mkdir -p .catpaw/memory

# 检查 .gitignore
grep -q ".catpaw/" .gitignore || echo ".catpaw/" >> .gitignore
```

写入初始快照：

```markdown
## 🧠 车机研发 Workflow 快照 — [需求名称] @ [YYYY-MM-DD]

### 需求概要
[用户原始需求的 2-3 句摘要]

### 公共参数
- citadel_parent_id: <id>
- 起始阶段: <A/B/C>

### 阶段进度
- [ ] Phase-1 需求分析 → 状态: 待执行
- [ ] Phase-2 技术评审 → 状态: 待执行
- [ ] Phase-3 开发 → 状态: 待执行

### 阶段产出（由主 Agent 在每阶段完成后更新）
| 阶段 | 输出文档 | 关键结论 | 用户问题 |
|------|---------|---------|---------|
| 需求分析 | 待执行 | — | — |
| 技术评审 | 待执行 | — | — |
| 开发 | 待执行 | — | — |

### 代码产出
- 分支: —
- 提交: —
```

### 更新时机

| 时机 | 操作 |
|------|------|
| Phase-N SubAgent 返回 Summary 且用户确认后 | 更新对应阶段的「阶段产出」行，标记为 ✅ |
| 用户提问并 SubAgent 给出回答后 | 在对应阶段的「用户问题」列追加 `Q: ... → A: ...（≤20字）` |
| Phase-3 完成后 | 更新「代码产出」中的分支和提交哈希 |

### 分层读取规则（主 Agent 使用）

```
优先级 1（首选）：阅读 SubAgent 返回的 Summary（≤200字）
  → 若 Summary 信息足够回答用户问题或推进流程，直接使用

优先级 2（按需）：read_file memory 快照
  → 仅当以下情况触发：
    · 用户要求回顾某阶段的完整结论
    · 需要向新 SubAgent 注入前置阶段的详细上下文
    · 主 Agent 当前 context 不足以重建阶段信息
    · 用户问「之前那个问题 AI 是怎么回答的」

⛔ 禁止：在 Summary 已足够的情况下仍然主动读取 memory，
   这会污染主 Agent 上下文，与 O-W 模式的上下文节约原则矛盾。
```

---

## 流程记录维护规则

> Init 确认后，主 Agent 同时在内存（当前对话上下文）维护「流程记录」，以及在 memory 快照中持久化。内存版本用于当前流程推进；快照版本用于跨阶段恢复和 SubAgent 上下文注入。

**流程记录结构（内存中维护）**：

```
workflow_record = {
  需求名称: <name>,
  citadel_parent_id: <id>,
  起始阶段: <A/B/C>,
  开始时间: <YYYY-MM-DD>,
  memory_snapshot_path: ".catpaw/memory/car-workflow-<slug>-snapshot.md",
  阶段记录: [
    {
      阶段: "需求评审",
      输入信息: "<用户原始需求摘要>",
      输出文档: "<link or 未执行>",
      用户问题: ["<用户在本阶段提出的具体问题列表>"],
      状态: "待执行 / 完成 / 已跳过"
    },
    {
      阶段: "技术评审",
      输入信息: "<需求评审文档链接 or 已跳过>",
      输出文档: "<link or 未执行>",
      用户问题: [],
      状态: "待执行"
    },
    {
      阶段: "开发自测",
      输入信息: "<技术评审文档链接 or 已跳过>",
      输出文档: "<代码评审+测试用例链接 or 未执行>",
      用户问题: [],
      状态: "待执行"
    },
    {
      阶段: "知识库同步",
      输入信息: "<开发自测代码分支 + 提交哈希>",
      输出文档: "<知识库更新说明链接 or 未执行>",
      用户问题: [],
      知识库变更摘要: "",
      状态: "待执行"
    },
    {
      阶段: "打包提测",
      输入信息: "*(请手动填写)*",
      输出文档: "*(请手动填写)*",
      用户问题: [],
      状态: "手动"
    }
  ],
  代码分支: "",
  提交哈希: ""
}
```

**用户问题追加规则**：
- 每当用户在某阶段提出具体问题，主 Agent 在 `workflow_record.阶段记录[N].用户问题` 和 memory 快照中同步追加
- 格式：`"Q: <用户问题> | A: <SubAgent 回答摘要，≤20字>"`

**更新时机**：
- 每个阶段 SubAgent 返回 SUMMARY 且用户确认后，立即更新内存记录和 memory 快照
- Phase-3 完成后更新 `代码分支` 和 `提交哈希`
- Phase-4 完成后更新 `阶段记录[知识库同步].输出文档` 和 `知识库变更摘要`

---

## SubAgent 通信协议

> 本协议定义主 Agent（Orchestrator）与 SubAgent（Worker）之间的信息传递规范，节约主 Agent 上下文。

### 主 Agent → SubAgent（启动参数）

启动 SubAgent 时，在 `task.prompt` 中传入以下结构化上下文（自包含，不依赖对话历史）：

```
=== WORKFLOW HANDOFF ===
来自：meituan-car-ai-workflow 主 Agent（Orchestrator）
阶段：Phase [N] - [阶段名称]

公共参数：
- citadel_parent_id: <id>
- 需求名称: <name>

阶段输入：
- <上一阶段产出或用户原始需求>

执行要求：
- 完整执行 [skill名称] skill 的全部步骤
- 内部交叉验证通过创建 Sub-SubAgent（task 工具）完成
- 产出文档写入 citadel_parent_id
- 完成后输出标准 Summary（见下方格式）
- 学城目录已由 workflow 提供，不得再次询问用户

Summary 格式（必须按此格式输出，作为最终返回结果）：
=== PHASE [N] SUMMARY ===
状态：✅ 完成 / ⚠️ 完成（有问题） / ❌ 失败
产出文档：[标题] → https://km.sankuai.com/collabpage/[id]
关键结论：（≤3条，每条≤30字）
  · [结论1]
  · [结论2]
  · [结论3]
待确认问题：（如有）
  · [问题1]
  · [问题2]
交叉验证结果：✅ 通过 / ⚠️ 发现 [N] 处问题（已修正）
=== END SUMMARY ===
```

> ⚠️ 上下文注入原则（来自 O-W 模式）：注入 SubAgent 的每个 token 必须是有效信号。前置阶段产出超过 1000 tokens 时，主 Agent 从 memory 快照中提炼精华后注入，而非全量粘贴原始内容。

### SubAgent → 主 Agent（返回 Summary）

SubAgent 的**最终返回消息**必须严格按照上方 Summary 格式输出。
主 Agent 只读此 Summary，不翻阅 SubAgent 的执行过程，不在主 context 积累代码或文档细节。

### 主 Agent 处理规则

```
IF SubAgent 返回 Summary THEN
  1. 向用户展示 Summary
  2. 更新内存中 workflow_record 和 memory 快照
  3. 询问「是否有问题？是否继续下一阶段？」
  4. 等待用户明确确认
  IF 用户说「有问题，需要详细查看」THEN
    resume SubAgent 并传达问题描述
    等待 SubAgent 补充说明或修正
  ELSE IF 用户确认通过 THEN
    回填总览表 → 推进下一阶段
END
```

---

## Phase 1：需求分析阶段

**触发条件**：起始阶段为 A

### 主 Agent 操作

启动 SubAgent（**不阻塞主 Agent 上下文**）：

```
task(
  description: "Phase-1 需求分析",
  subagent_type: "general-agent",
  prompt: """
=== WORKFLOW HANDOFF ===
来自：meituan-car-ai-workflow 主 Agent（Orchestrator）
阶段：Phase 1 - 需求分析

公共参数：
- citadel_parent_id: <citadel_parent_id>
- 需求名称: <需求名称>

阶段输入：
- 需求信息: <Init 收集的完整需求描述>

执行要求：
1. 读取 car-requirement-analysis skill（路径：~/.catpaw/skills/skills-market/car-requirement-analysis/SKILL.md，备选：~/.claude/skills/car-requirement-analysis/SKILL.md）
2. 完整执行 skill 的需求分析步骤
3. 交叉验证：创建一个 Sub-SubAgent（task 工具，subagent_type: general-agent）对需求评审文档进行复核，检查：
   · 需求范围是否遗漏
   · 实现平台（鸿蒙/安卓/iOS/MRN/MSC）是否明确
   · 排期是否合理
   Sub-SubAgent 的复核结论必须在修订文档时体现
4. 每到需要用户确认的节点，立即输出对应 PENDING 格式后停止，等待主 Agent resume
5. 所有 PENDING 用户均确认后，再产出需求评审文档，写入 citadel_parent_id
6. ⛔ 禁止"需求合理性评估结论直接自行决定继续"——⚠️/❌ 结论必须暴露给用户
7. 学城目录已由 workflow 提供，不得再次询问用户

PENDING 输出格式参见 car-requirement-analysis skill 的 SubAgent 模式分段返回协议。

所有 PENDING 用户确认完毕后的最终 Summary 格式：
=== PHASE 1 SUMMARY ===
状态：✅ 完成 / ⚠️ 完成（有问题） / ❌ 失败
产出文档：[标题] → https://km.sankuai.com/collabpage/[id]
关键结论：
  · [需求范围一句话]
  · [实现平台]
  · [排期]
待确认问题：（如有）
  · [问题]
交叉验证结果：✅ 通过 / ⚠️ 发现 [N] 处问题（已修正）
=== END SUMMARY ===
"""
)
```

### 主 Agent 处理 Phase-1 SubAgent 返回的逻辑

Phase-1 SubAgent 每次返回只会有两种格式：**PHASE 1 PENDING-x** 或 **PHASE 1 SUMMARY**。

**主 Agent 必须按如下循环处理，直到收到 PHASE 1 SUMMARY：**

```
LOOP:
  SubAgent 返回内容
  │
  ├─ 包含 "=== PHASE 1 PENDING-x ===" ？
  │   ├─ 是 → SubAgent 已直接向用户输出确认请求，⛔ 主 Agent 禁止重复输出任何 PENDING 内容，直接等待用户反馈：
  │   │        ┌─ 用户继续/确认 → resume Phase-1 SubAgent
  │   │        │   prompt: "[用户继续] 请继续执行" 或 "[用户确认] 请写入学城并输出 SUMMARY"
  │   │        └─ 用户调整/修改 → resume Phase-1 SubAgent
  │   │            prompt: "[用户调整: {调整意见}]" 或 "[用户修改: {修改意见}]"
  │   └─ 继续 LOOP
  │
  └─ 包含 "=== PHASE 1 SUMMARY ===" ？
      └─ 是 → 退出 LOOP，执行"主 Agent 收到最终 Summary 后"逻辑
```

### 主 Agent 收到最终 PHASE 1 SUMMARY 后

1. 向用户展示 Summary
2. **更新 memory 快照**（Phase-1 阶段产出行）
3. 询问确认：

```
📋 需求分析阶段完成，SubAgent 产出摘要如上。

❓ 是否有需要进一步确认的问题？
   · 如需查看详情，请说「查看详情」或描述具体问题
   · 如确认无误，请回复「继续技术评审」
```

4. 若用户提出问题 → resume Phase-1 SubAgent，传达问题，等待补充说明；同时将问题和回答追加到 `workflow_record.阶段记录[需求评审].用户问题` 和 memory 快照
5. 若用户确认 → 更新内存中 `workflow_record`（需求评审行的输出文档、状态），推进 Phase 2

---

## Phase 2：技术评审阶段

**触发条件**：起始阶段为 A（Phase 1 确认后）或 B

### 主 Agent 操作

启动 SubAgent，**注意**：若需注入 Phase-1 产出上下文，优先用 Summary 中的「关键结论」（≤3条），仅当关键结论不足时才从 memory 快照提炼后注入：

```
task(
  description: "Phase-2 技术评审",
  subagent_type: "general-agent",
  prompt: """
=== WORKFLOW HANDOFF ===
来自：meituan-car-ai-workflow 主 Agent（Orchestrator）
阶段：Phase 2 - 技术评审

公共参数：
- citadel_parent_id: <citadel_parent_id>
- 需求名称: <需求名称>

阶段输入：
- 需求分析结论: <Phase 1 产出的需求评审文档链接 或 用户提供内容>

执行要求：
1. 读取 car-tech-review skill（路径：~/.catpaw/skills/skills-market/car-tech-review/SKILL.md，备选：~/.claude/skills/car-tech-review/SKILL.md）
2. 完整执行 skill 的技术评审步骤，包括读取相关代码仓库
3. 交叉验证：创建一个 Sub-SubAgent（task 工具，subagent_type: general-agent）对技术评审文档进行复核，检查：
   · 改动范围是否准确（文件级别）
   · 风险点是否完整
   · 测试方案是否可执行
   Sub-SubAgent 的复核结论必须在修订文档时体现
4. 每到需要用户确认的节点，立即输出对应 PENDING 格式后停止，等待主 Agent resume
5. 所有 PENDING 用户均确认后，再产出技术评审文档，写入 citadel_parent_id
6. ⛔ 禁止"检测到需求变更但自行决定继续"——变更摘要必须暴露给用户确认
7. 学城目录已由 workflow 提供，不得再次询问用户

PENDING 输出格式参见 car-tech-review skill 的 SubAgent 模式分段返回协议。

所有 PENDING 用户确认完毕后的最终 Summary 格式：
=== PHASE 2 SUMMARY ===
状态：✅ 完成 / ⚠️ 完成（有问题） / ❌ 失败
产出文档：[标题] → https://km.sankuai.com/collabpage/[id]
关键结论：
  · [改动文件数/模块]
  · [主要风险点]
  · [测试方案类型]
待确认问题：（如有）
  · [问题]
交叉验证结果：✅ 通过 / ⚠️ 发现 [N] 处问题（已修正）
=== END SUMMARY ===
"""
)
```

### 主 Agent 处理 Phase-2 SubAgent 返回的逻辑

Phase-2 SubAgent 每次返回只会有两种格式：**PHASE 2 PENDING-x** 或 **PHASE 2 SUMMARY**。

**主 Agent 必须按如下循环处理，直到收到 PHASE 2 SUMMARY：**

```
LOOP:
  SubAgent 返回内容
  │
  ├─ 包含 "=== PHASE 2 PENDING-x ===" ？
  │   ├─ 是 → SubAgent 已直接向用户输出确认请求，⛔ 主 Agent 禁止重复输出任何 PENDING 内容，直接等待用户反馈：
  │   │        ┌─ 用户继续/确认 → resume Phase-2 SubAgent
  │   │        │   prompt: "[用户继续] 请继续执行" 或 "[用户确认] 请写入学城并输出 SUMMARY"
  │   │        └─ 用户调整/修改 → resume Phase-2 SubAgent
  │   │            prompt: "[用户调整: {调整意见}]" 或 "[用户修改: {修改意见}]"
  │   └─ 继续 LOOP
  │
  └─ 包含 "=== PHASE 2 SUMMARY ===" ？
      └─ 是 → 退出 LOOP，执行"主 Agent 收到最终 Summary 后"逻辑
```

### 主 Agent 收到最终 PHASE 2 SUMMARY 后

1. 向用户展示 Summary
2. **更新 memory 快照**（Phase-2 阶段产出行）
3. 询问确认：

```
📐 技术评审阶段完成，SubAgent 产出摘要如上。

❓ 是否有需要进一步确认的问题？
   · 如需查看详情，请说「查看详情」或描述具体问题
   · 如确认无误，请回复「继续开发」
```

4. 若用户提出问题 → resume Phase-2 SubAgent，传达问题，等待补充说明；同时将问题和回答追加到 `workflow_record.阶段记录[技术评审].用户问题` 和 memory 快照
5. 若用户确认 → 更新内存中 `workflow_record`（技术评审行的输出文档、状态），推进 Phase 3

---

## Phase 3：开发阶段

**触发条件**：起始阶段为 A（Phase 2 确认后）、B（Phase 2 确认后）或 C

### 主 Agent 操作

启动 SubAgent，**注意**：向 Phase-3 SubAgent 注入前置阶段上下文时，优先使用各阶段 Summary 的「关键结论」，避免全量粘贴历史文档内容：

```
task(
  description: "Phase-3 开发",
  subagent_type: "general-agent",
  prompt: """
=== WORKFLOW HANDOFF ===
来自：meituan-car-ai-workflow 主 Agent（Orchestrator）
阶段：Phase 3 - 开发

公共参数：
- citadel_parent_id: <citadel_parent_id>
- 需求名称: <需求名称>

阶段输入：
- 技术评审结论: <Phase 2 产出的技术评审文档链接 或 用户提供内容>

执行要求：
1. 读取 car-development-guide skill（路径：~/.catpaw/skills/skills-market/car-development-guide/SKILL.md，备选：~/.claude/skills/car-development-guide/SKILL.md）
2. 完整执行 skill 的开发流程（含工作量评估 → CheckPoint 拆分 → 编码 → 自查）
3. 交叉验证：每个 CheckPoint 编码完成后，创建一个 Sub-SubAgent（task 工具，subagent_type: general-agent）进行代码评审，检查：
   · 是否遵守项目编码规范（读取 AGENTS.md / .mrules）
   · 是否有明显的逻辑错误或遗漏
   · 接口签名是否与技术评审一致
   Sub-SubAgent 的评审意见必须在修正代码后体现
4. 每完成一个 CheckPoint（包括 CheckPoint 0 工作量评估），立即输出 CHECKPOINT PENDING 格式后停止
5. 所有 CheckPoint 用户均确认后，再产出代码评审文档 + 测试用例文档，写入 citadel_parent_id
6. ⛔ 禁止"CheckPoint 间的用户确认由本 SubAgent 直接向用户请求"——SubAgent 无此能力，必须通过 PENDING + resume 机制
7. 学城目录已由 workflow 提供，不得再次询问用户

CHECKPOINT PENDING 输出格式（每完成一个 CheckPoint 必须输出此格式后停止）：
=== CHECKPOINT [N] PENDING ===
状态：⏸️ 等待用户确认
CheckPoint 名称：[名称]
已完成内容：
  · 文件 A：[改动摘要]
subagent 审查：[通过 / N 个问题已修复]
关键实现说明：[非直觉设计决策，无则写"无"]
---
⏸️ 主 Agent：请将以上 CheckPoint [N] 完成情况展示给用户，等待用户明确确认后再 resume 本 SubAgent 继续。
用户确认信号：收到用户"继续"/"OK"/"确认"后 resume，prompt 中包含 `[用户确认]`
用户提问信号：收到用户问题后 resume，prompt 中包含 `[用户问题: xxx]`
=== END CHECKPOINT [N] PENDING ===

所有 CheckPoint 确认完毕后的最终 Summary 格式：
=== PHASE 3 SUMMARY ===
状态：✅ 完成 / ⚠️ 完成（有问题） / ❌ 失败
产出文档：
  · 代码评审 → https://km.sankuai.com/collabpage/[id]
  · 测试用例 → https://km.sankuai.com/collabpage/[id]
代码产出：
  · 分支: [branch-name]
  · 提交: [commit-hash]
  · CheckPoint 数: [N]
关键结论：
  · [主要改动一句话]
  · [测试覆盖情况]
待确认问题：（如有）
  · [问题]
交叉验证结果：✅ 通过 / ⚠️ 发现 [N] 处问题（已修正）
=== END SUMMARY ===
"""
)
```

### 主 Agent 处理 Phase-3 SubAgent 返回的逻辑

Phase-3 SubAgent 每次返回只会有两种格式：**CHECKPOINT PENDING** 或 **PHASE 3 SUMMARY**。

**主 Agent 必须按如下循环处理，直到收到 PHASE 3 SUMMARY：**

```
LOOP:
  SubAgent 返回内容
  │
  ├─ 包含 "=== CHECKPOINT [N] PENDING ===" ？
  │   ├─ 是 → SubAgent 已直接向用户输出 CheckPoint 完成情况，⛔ 主 Agent 禁止重复输出任何 PENDING 内容，直接等待用户反馈：
  │   │        ┌─ 用户确认（"继续"/"OK"/"确认"）
  │   │        │   → resume Phase-3 SubAgent
  │   │        │     prompt: "[用户确认] 请继续执行 CheckPoint [N+1]"
  │   │        └─ 用户提出问题
  │   │            → resume Phase-3 SubAgent
  │   │              prompt: "[用户问题: {用户描述的问题}] 请针对 CheckPoint [N] 修复后重新输出 PENDING"
  │   └─ 继续 LOOP
  │
  └─ 包含 "=== PHASE 3 SUMMARY ===" ？
      └─ 是 → 退出 LOOP，执行"主 Agent 收到最终 Summary 后"逻辑
```

### 主 Agent 收到最终 PHASE 3 SUMMARY 后

1. 向用户展示 Summary
2. **更新 memory 快照**（Phase-3 阶段产出行、代码产出）
3. 询问确认：

```
💻 开发阶段完成，SubAgent 产出摘要如上。

❓ 是否有需要进一步确认的问题？
   · 如需查看详情，请说「查看详情」或描述具体问题
   · 如确认无误，请回复「完成」
```

4. 若用户提出问题 → resume Phase-3 SubAgent，传达问题，等待补充说明；同时将问题和回答追加到 `workflow_record.阶段记录[开发自测].用户问题` 和 memory 快照
5. 若用户确认 → 更新内存中 `workflow_record`（开发自测行的输出文档、代码分支、提交哈希），推进 Phase 4 知识库同步

---

## Phase 4：知识库同步阶段

**触发条件**：Phase 3 确认后自动进入

### 主 Agent 操作

启动 SubAgent，向 Phase-4 SubAgent 注入开发阶段的精简摘要、代码产出和现有知识库位置，避免把完整代码 diff 全量塞入上下文：

```
task(
  description: "Phase-4 知识库同步",
  subagent_type: "general-agent",
  prompt: """
=== WORKFLOW HANDOFF ===
来自：meituan-car-ai-workflow 主 Agent（Orchestrator）
阶段：Phase 4 - 知识库同步

公共参数：
- citadel_parent_id: <citadel_parent_id>
- 需求名称: <需求名称>

阶段输入：
- 开发阶段摘要: <Phase 3 Summary 的关键结论>
- 代码产出: <branch-name> / <commit-hash>

执行要求：
1. 完整执行知识库增量同步流程（见下方 Step 1~3）
2. 交叉验证：知识库文档更新完毕后，创建一个 Sub-SubAgent（task 工具，subagent_type: general-agent）对更新结果进行复核，检查：
   · docs/README.md 目录列表与实际文件是否一一对应
   · service-api-index.md 的 Service 数量是否与代码一致
   · 所有新增/更新文档是否包含完整 frontmatter
   Sub-SubAgent 的复核结论必须在修正后体现
3. 学城目录已由 workflow 提供，不得再次询问用户

【前置检查 — Node 环境】
写入学城前必须确认 Node >= 18（citadel CLI 依赖）：
```bash
nvm use 18
node -v  # 确认输出 v18.x 或更高
```

【Step 1 — 扫描变更文件】
基于 Phase 3 的代码变更，定位受影响的源文件：

```bash
# 以 docs/README.md 的修改时间为基准，找出比它更新的车机源文件（范围收窄到 src/）
find src/ -newer docs/README.md -name "*.java" | sort
find src/ -newer docs/README.md -name "*.kt" | sort
# 若包含前端层：
find src/ -newer docs/README.md \( -name "*.ts" -o -name "*.tsx" \) \
  | grep -v node_modules | grep -v ".test." | grep -v __tests__ | sort
```

若 docs/ 目录尚不存在（首次同步），则读取 AGENTS.md（若存在）中的「模块划分」或「目录结构」章节，结合本次开发的全量变更文件作为扫描范围。

【Step 2 — 提取知识要点（confidence: L1 优先）】
分批读取变更文件（每批 3-5 个），提取：
- 新增/变更的接口签名（Controller / Router / RPC / Service 方法）
- 新增/变更的关键数据模型、枚举
- 新增/变更的 UI 组件（若有前端层）
- 废弃或删除的模块/接口（需标注废弃原因）
- 反直觉设计或已知坑（写入 implicit-knowledge.md）

代码与已有文档冲突时：代码(L1) 优先，冲突处标注 `[⚠️ 可能过时，以代码为准]`；不确定内容标注 `[待确认]`，绝不编造。

【Step 3 — 更新知识库文档（写入 citadel_parent_id）】
按以下优先级和顺序依次更新（使用 oa-skills citadel 工具写入学城）：

P0（必须更新，有变更必做）：
1. `docs/service-api-index.md` — 接口 / RPC / Service 速查索引（若无则新建）；Service 数量须与 `find src/ -name "*Service.java" | wc -l` 结果一致
2. `docs/file-index.md` — 全量文件路径索引（同步新增/删除文件）
3. `docs/quick-lookup.md` — 场景 → 文件路径速查（若无则新建）
4. `docs/README.md` — 更新目录列表 + 可检索范围表格（文件数量变化）⚠️ 最常遗漏，必须同步

P1（按需更新，有实质变化才更新）：
- `docs/architecture.md` — 若涉及模块架构或请求流程变化
- `docs/implicit-knowledge.md` — 有新已知坑时追加（至少累计 5 条）
- `AGENTS.md` — 若本次开发引入新的编码约束或填坑经验，追加到对应章节

【失效知识处理规则】
- 优先归档（移入 `docs/archive/` 目录），不直接物理删除
- 若确需删除，必须在 Summary 中单列删除原因和影响范围

【交付前校验】
- `docs/README.md` 目录列表与实际文件一一对应（无遗漏、无幽灵条目）
- `service-api-index.md` 中的 Service 数量 == `find src/ -name "*Service.java" | wc -l`
- 所有新增/更新文档头部有完整 YAML frontmatter（topic/keywords/triggers/confidence/source/updated）
- 若有 `[待确认]` 标注，必须在 Summary 中列清单汇报
- ⛔ 不得向用户重新询问学城目录（citadel_parent_id 已由 HANDOFF 传入）

最终 Summary 格式：
=== PHASE 4 SUMMARY ===
状态：✅ 完成 / ⚠️ 完成（有问题） / ❌ 失败
产出文档：知识库更新说明 → https://km.sankuai.com/collabpage/[id]
关键结论：
  · 新增: [N] 项（列举文件名）
  · 更新: [N] 项（列举文件名）
  · 归档/删除: [N] 项（列举文件名 + 原因）
待确认问题：（如有）
  · [问题]
校验结果：✅ 一致性通过 / ⚠️ 发现 [N] 项待确认
交叉验证结果：✅ 通过 / ⚠️ 发现 [N] 处问题（已修正）
=== END SUMMARY ===
"""
)
```

### 主 Agent 处理 Phase-4 SubAgent 返回的逻辑

Phase-4 SubAgent 的最终返回消息必须为 `PHASE 4 SUMMARY`。

**主 Agent 必须按如下逻辑处理，直到收到 PHASE 4 SUMMARY：**

```
LOOP:
  SubAgent 返回内容
  │
  └─ 包含 "=== PHASE 4 SUMMARY ===" ？
      ├─ 否 → SubAgent 仍在执行（知识库同步无中间 PENDING 节点），继续等待
      └─ 是 → 退出 LOOP，执行"主 Agent 收到最终 Summary 后"逻辑
```

### 主 Agent 收到最终 PHASE 4 SUMMARY 后

1. 向用户展示 Summary
2. **更新 memory 快照**（Phase-4 阶段产出行、知识库变更摘要）
3. 询问确认：

```
📚 知识库同步阶段完成，SubAgent 产出摘要如上。

❓ 是否有需要进一步确认的问题？
   · 如需查看详情，请说「查看详情」或描述具体问题
   · 如确认无误，请回复「完成」
```

4. 若用户提出问题 → resume Phase-4 SubAgent，传达问题，等待补充说明；同时将问题和回答追加到 `workflow_record.阶段记录[知识库同步].用户问题` 和 memory 快照
5. 若用户确认 → 更新内存中 `workflow_record`（知识库同步行的输出文档、状态、知识库变更摘要），输出全流程汇总

---

## 全流程汇总输出

**第一步：根据 `workflow_record` 生成总览文档内容并写入学城**

> ⚠️ 若需要回顾某阶段完整信息，此时可 read_file memory 快照，将其作为总览文档生成的信息源。

总览文档模板（根据实际执行的阶段填写，未执行的阶段行写「已跳过」）：

````markdown
# [需求名称] AI工作流总览

> 创建时间：[YYYY-MM-DD]
> 学城文档目录：https://km.sankuai.com/collabpage/[citadel_parent_id]

## 研发流程进度跟踪

| 阶段 | 输入信息 | 输出文档 | 用户问题 |
|------|---------|---------|----------|
| 需求评审 | [需求评审输入摘要] | [文档链接 或 已跳过] | [用户提出的问题，无则写「无」] |
| 技术评审 | [需求评审文档链接 或 已跳过] | [文档链接 或 已跳过] | [用户问题] |
| 开发自测 | [技术评审文档链接 或 已跳过] | [代码评审+测试用例链接 或 已跳过] | [用户问题] |
| 知识库同步 | [开发自测代码分支 + 提交] | [知识库更新说明链接 或 已跳过] | [用户问题] |
| 打包提测 | *(请手动填写)* | *(请手动填写)* | *(请手动填写)* |

## 代码产出

- 分支：[branch-name 或 已跳过]
- 提交：[commit-hash 或 已跳过]
````

> **「用户问题」列填写规则**：
> - 若用户在该阶段提出过具体问题，每条格式为：`Q: <问题> → A: <回答摘要>`，多条用换行分隔
> - 若无问题，写「无」
> - 「打包提测」行由人工填写，AI 不得填入任何内容

```bash
# 执行前确认 Node.js >= 20
node -v  # 不满足则 nvm use 20

oa-skills citadel createDocument \
  --title "[需求名称] AI工作流总览" \
  --parentId <citadel_parent_id> \
  --file /tmp/workflow_overview.md
```

**第二步：更新 memory 快照状态为「已完成」**

在 memory 快照末尾追加：
```
### 完成记录
- 完成时间: [YYYY-MM-DD]
- 总览文档: https://km.sankuai.com/collabpage/[id]
- 状态: ✅ 全流程完成
```

**第三步：向用户输出汇总**

```
🎉 全流程完成

AI工作流总览文档：https://km.sankuai.com/collabpage/[overview_content_id]

已产出文档：
- 📋 AI工作流总览：https://km.sankuai.com/collabpage/[id]
- 📄 [需求名称]需求评审：https://km.sankuai.com/collabpage/[id]（或「已跳过」）
- 📐 [需求名称]技术评审：https://km.sankuai.com/collabpage/[id]（或「已跳过」）
- 🔍 [需求名称]代码评审：https://km.sankuai.com/collabpage/[id]（或「已跳过」）
- ✅ [需求名称]测试用例：https://km.sankuai.com/collabpage/[id]（或「已跳过」）
- 📚 [需求名称]知识库更新说明：https://km.sankuai.com/collabpage/[id]（或「已跳过」）

代码分支：<分支名>
提交：<commit hash>

⚠️ 请手动填写总览文档中「打包提测」行的信息
```

---

## 主 Agent 与 SubAgent 通信：问题传达流程

当用户在某阶段提出问题或疑虑时，主 Agent 执行以下步骤：

```
1. 主 Agent 将用户问题整理为结构化描述：
   「用户对 Phase [N] 提出以下问题：
   · [问题描述]
   请针对上述问题补充说明或修正，并更新文档。
   完成后按原 Summary 格式重新输出。」

2. resume Phase-[N] SubAgent，传入上述问题描述

3. SubAgent 处理后重新输出 Summary（带修正标注）

4. 主 Agent 再次向用户展示更新后的 Summary

5. 同步将问题/回答追加到 memory 快照

6. 重复确认流程，直到用户批准
```

---

## 阶段间衔接规则

| 情况 | 处理方式 |
|------|---------|
| 用户说「暂停」 | 记录当前阶段和 SubAgent agentId，**更新 memory 快照**（记录暂停时间和待恢复的 agentId），等待用户重新激活后 resume |
| 用户说「跳过 XX 阶段」 | 确认后跳过，提示总览表该行将缺失 |
| SubAgent 返回失败状态 | 主 Agent 展示错误摘要，询问用户是否重试 |
| 文档写入学城失败 | SubAgent 在 Summary 中标注，主 Agent 报告给用户，不自动推进 |
| 总览文档回填失败 | 说明哪一行未回填，继续推进，汇总时提示手动补充 |
| 用户在技术评审修改需求 | 提示是否需要 resume Phase-1 SubAgent 重新分析 |
| **新对话窗口恢复任务** | 主 Agent 首先 read_file memory 快照，从「阶段进度」恢复状态，再按需 resume 对应 SubAgent |

---

## 关键约束

- **主 Agent 上下文节约（O-W 核心原则）**：只读 SubAgent Summary（≤200字），不直接执行各阶段 skill 的具体操作，不在自己 context 积累代码或文档片段
- **SubAgent 自包含执行**：每个 SubAgent（Worker）独立完成阶段任务，task.prompt 必须包含完整上下文（不依赖对话历史）；内部可创建 Sub-SubAgent 做交叉验证
- **Memory 持久化**：主 Agent 在 `.catpaw/memory/` 维护快照，Summary 优先于读文件，快照用于跨阶段恢复和必要时的上下文补充
- **问题传达机制**：用户的疑问通过 resume SubAgent 传达，不由主 Agent 代为解决
- **阶段间必须等待用户确认**：每个阶段 Summary 展示后，等待用户批准才推进
- **学城目录只收集一次**：Init 阶段确定，通过 HANDOFF 参数传给所有 SubAgent
- **总览文档在全流程结束时创建**：全流程汇总时根据 `workflow_record` 一次性生成并写入学城，不在 Init 阶段提前创建

---

## 反模式（禁止行为）

| # | 禁止行为 | 原因 |
|---|---------|------|
| AP-1 | Init 未完成就启动 SubAgent | 公共参数必须先收集完毕 |
| AP-2 | 主 Agent 直接执行阶段 skill 的具体操作（不走 SubAgent） | 违反 O-W 模式，Orchestrator 只做调度决策通信，所有实现 100% 交由 Worker |
| AP-3 | 主 Agent 阅读 SubAgent 执行过程细节（非 Summary） | 除非用户要求，主 Agent 只看 Summary |
| AP-4 | SubAgent 完成后自动推进，不等用户确认 | 阶段间推进需用户知晓和批准 |
| AP-5 | SubAgent 再次询问学城目录 | `citadel_parent_id` 已由 HANDOFF 参数传入 |
| AP-6 | 为打包提测行填写任何 AI 生成内容 | 打包提测是人工阶段 |
| AP-7 | 用户提问时主 Agent 自行解答而不 resume SubAgent | 问题应传达给对应 SubAgent，保持上下文一致 |
| AP-8 | 向用户索要多个不同的学城链接 | 只需一个 `citadel_parent_id` |
| AP-9 | 研发流程入口自动执行版本检查/更新 | 环境管理操作只在用户主动触发时运行 |
| AP-10 | 用户未触发环境管理时主动提示 skill 有更新 | 版本提示属于干扰信息 |
| AP-11 | 主 Agent 替 SubAgent 做交叉验证 | 交叉验证必须由 SubAgent 创建 Sub-SubAgent 完成 |
| AP-12 | Phase-3 SubAgent 完成所有 CheckPoint 后才输出一次 Summary | SubAgent 必须每个 CheckPoint 完成后立即输出 PENDING 并停止，等待 resume |
| AP-13 | 主 Agent 收到 CHECKPOINT PENDING 后自动 resume 不等用户确认 | PENDING 后必须向用户展示并等待明确确认，不可自动推进 |
| AP-14 | Phase-1/2 SubAgent 在需要用户确认的节点不输出 PENDING 直接执行 | 需求合理性评估⚠️/❌、技术评审变更检测、Confirmation Gate 均须 PENDING |
| AP-15 | 主 Agent 收到 PHASE 1/2 PENDING 后自动 resume 不等用户确认 | 与 AP-13 相同原则，三个阶段均不可自动推进 |
| AP-16 | Init 阶段 3️⃣ 未回答时自行默认从 A 开始 | 起始阶段必须由用户明确选择，AI 不得代替用户决策 |
| AP-17 | 主 Agent 将 SubAgent PENDING 内容再次转发给用户（包括以「摘要」「整理」「帮助用户理解」「格式化展示」等任何形式的变体转发） | SubAgent 输出用户可直接看到，任何形式的重复输出均违反本条。**每次向用户输出前必须自检：我即将输出的内容是否包含 SubAgent 已输出的 PENDING 片段？若是，立即停止，仅等待用户反馈后 resume SubAgent。** |
| AP-18 | 在 Init 阶段或研发过程中提前创建总览文档 | 总览文档须在全流程结束后根据完整记录一次性创建，提前创建会导致信息不完整 |
| AP-19 | Summary 已足够时仍主动读取 memory 快照 | 违反 O-W 上下文节约原则，memory 读取只在 Summary 信息不足时按需触发 |
| AP-20 | 向 SubAgent 注入超过 1000 tokens 的前置阶段原始内容 | 应从 memory 快照提炼精华后注入，确保 Worker 上下文精华化 |
| AP-21 | Orchestrator 在自己 context 积累代码片段、文档全文或 SubAgent 执行细节 | context 爆炸的根源，违反 O-W 核心约束 |
| AP-22 | 知识库缺失（AGENTS.md / .mrules / docs 学城目录）且用户未明确选择 B/C 时自动继续研发流程 | 缺少项目上下文会导致 AI 产出质量严重下降，必须经用户知晓风险并主动确认才可继续 |
| AP-23 | Phase-4 SubAgent 再次询问学城目录 | `citadel_parent_id` 已由 HANDOFF 参数传入，不得重复询问 |
| AP-24 | Phase-4 SubAgent 直接物理删除失效文档而不归档 | 失效知识必须优先归档至 `docs/archive/`，删除须在 Summary 中注明原因 |
