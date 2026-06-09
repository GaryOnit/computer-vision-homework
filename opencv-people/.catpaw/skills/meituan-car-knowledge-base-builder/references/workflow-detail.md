# 知识库建设操作手册

## 0. 信息范围定义文档（阶段 0.5 操作手册）

### 0.1 什么是「信息范围定义文档」

这是**建库前必须由用户提供的前置输入**，类似一份"信息地图"，告诉 AI 本次建库可以去哪些地址获取信息。

**参考样例**：`km.sankuai.com/collabpage/2758014734`（data-service 已有文档）

该文档按七个层次组织，每层列出信息类型和来源地址：

| 层级 | 信息类型 | 示例来源 |
|------|---------|---------|
| 一、代码层 | 项目代码、相关仓库、构建配置 | `../meituan-car-core` DevTools 链接 |
| 二、变更历史层 | Git Log、MR/PR 列表 | `dev.sankuai.com/code/.../mr/list` |
| 三、需求/任务层 | ONES 工作项 | `km.sankuai.com/collabpage/2758501813` |
| 四、文档层 | 学城 API 总览、技术方案 | `km.sankuai.com/collabpage/2731851958` |
| 五、开发者输入层 | 代码注释约定 | 对话提供 |
| 六、运行时/线上层 | Raptor 项目、AppID、Horn | `MeituanCar`, AppID `551` |
| 七、AI辅助生成层 | 历史问答沉淀路径 | `.catpaw/memory/` |

### 0.2 如果用户未提供该文档

MUST 暂停并索取，输出以下提示：

```
在开始建库前，请提供本项目的「可检索信息范围定义」文档。

该文档需覆盖以下各层（每层注明来源地址）：
  一、代码层       — 项目代码、相关仓库、构建配置来源
  二、变更历史层   — Git Log、MR / PR、Changelog 来源
  三、需求/任务层  — ONES 工作项链接（spaceId）
  四、文档层       — 学城 API 总览、技术方案、接口协议文档链接
  五、开发者输入层 — 代码注释约定说明
  六、运行时/线上层— Raptor 项目名、AppID、Horn 配置说明
  七、AI辅助生成层 — 历史问答沉淀路径

如果贵项目尚无此文档，可参考模板自行填写：
km.sankuai.com/collabpage/2758014734

也可以直接将以上信息以文字形式提供给我。
```

### 0.3 解析文档并构建检索清单

收到信息范围定义文档后（学城链接则用 `oa-skills citadel getMarkdown` 读取），解析每层内容，构建带有来源地址的检索清单：

```bash
# 读取信息范围定义文档
nvm use 18 && oa-skills citadel getMarkdown --id <scope_doc_id> 2>&1
```

从文档中提取并填写检索清单表格：

```markdown
| 层级 | 信息类型 | 来源地址/路径 | 可信度 | 访问状态 |
|------|---------|------------|--------|--------|
| 一、代码层 | 项目代码 | `data-service/src/` | L1 | ✅ |
| 一、代码层 | meituan-car-core | `DevTools URL` | L1 | ❌ 外部仓库无权限，已跳过 |
| 二、变更历史层 | MR 列表 | `dev.sankuai.com/.../mr/list` | L2 | ✅ |
| 三、需求/任务层 | ONES 工作项 | spaceId=`46758` | L2 | ✅ |
| 四、文档层 | API 总览 | `km.sankuai.com/collabpage/2731851958` | L2 | ✅ |
| 四、文档层 | 技术方案 | `km.sankuai.com/collabpage/2753201585` | L2 | ✅ |
| 六、运行时层 | Raptor | `MeituanCar`, AppID=`551` | L2 | — 仅记录，不主动拉取 |
| 七、AI辅助层 | 历史问答 | `.catpaw/memory/` | L3 | ✅ |
```

### 0.4 验证清单中每条来源的可访问性

```bash
# 验证代码库
ls <repo>/src/main/java/ | head -5

# 验证学城文档（需先切 Node 18）
nvm use 18 && oa-skills citadel getDocInfo --id <document_id> 2>&1 | head -5

# 验证 ONES spaceId（需已登录）
ones filter-issues --project <spaceId> --limit 1 --fields "title" 2>&1

# 验证 Git MR（通过 web_fetch 访问）
# 若无权限则标注 ❌
```

### 0.5 无法访问时的暂停脚本

当任一资源返回错误，MUST 向用户输出并等待确认：

```
以下资源无法访问，请确认处理方式后继续：

❌ 学城文档 2731851958（来自信息范围文档第四层/API总览）：fetch failed
❌ ONES spaceId 46758（来自信息范围文档第三层）：Authentication failed

请选择：
(A) 提供替代链接或新的文档 ID
(B) 将内容文本直接粘贴给我
(C) 跳过该资源（知识库中标注"[未收录]"）
```

### 0.6 信息范围写入 docs/README.md 的格式

```markdown
## 可检索信息范围

> 来源：信息范围定义文档（km.sankuai.com/collabpage/2758014734）

| 层级 | 信息类型 | 来源 | 可信度 | 收录状态 |
|------|---------|------|--------|---------|
| 一、代码层 | 项目代码 src/ | 项目内 | L1 | ✅ 全量 <N> 个 .java 文件 |
| 一、代码层 | meituan-car-core | 外部仓库 | L1 | ❌ 未收录（无权限访问） |
| 三、需求/任务层 | ONES 工作项 | spaceId=46758 | L2 | ✅ 2026 Q1-Q2 共 23 条 |
| 四、文档层 | API 总览 | collabpage/2731851958 | L2 | ✅ |
| 四、文档层 | 技术方案 | collabpage/2753201585 | L2 | ✅ |
| 七、AI辅助层 | 历史问答 | .catpaw/memory/ | L3 | ✅ |
```

---

## 1. 工具初始化

### 1.1 Node 版本切换（citadel/ONES 必须）

```bash
nvm use 18
node --version  # 应输出 v18.x.x
```

**为什么 Node 14 不行？** `oa-skills citadel` 内部使用了全局 `fetch` API，Node 14 没有内置 fetch，会报 `ReferenceError: fetch is not defined`。

### 1.2 工具安装检查

```bash
which oa-skills   # citadel CLI
which ones        # ONES CLI
```

---

## 2. 学城（citadel）文档读取

### 2.1 获取文档内容

```bash
# 基础读取（适合 <200 行文档）
nvm use 18 && oa-skills citadel getMarkdown --id <document_id> 2>&1

# 大文档截断读取（防止 token 超限）
nvm use 18 && oa-skills citadel getMarkdown --id <document_id> 2>&1 | head -200

# 仅读取文档标题/目录（用于大文档导航）
nvm use 18 && oa-skills citadel getDocInfo --id <document_id> 2>&1

# 递归获取子文档列表
nvm use 18 && oa-skills citadel getChildContent --id <parent_document_id> 2>&1
```

### 2.2 文档 ID 来源

- URL 格式：`km.sankuai.com/collabpage/<id>` → id 即文档 ID
- 递归建库时：先用 `getChildContent` 获取子文档列表，再逐个读取

### 2.3 大文档处理策略

当文档 > 500 行时：
1. 先读前 200 行获取目录/导航
2. 根据目录识别"架构"、"API约定"等核心章节行号
3. 用 `offset`/`limit` 参数精准读取目标段落

### 2.4 文档内容可信度标注

学城文档内容写入 docs/ 时，必须标注：
- frontmatter 中 `confidence: L2`
- 如与代码冲突，具体冲突处标注 `[⚠️ 可能过时，以代码为准]`

---

## 3. ONES 工作项读取

### 3.1 过滤当前迭代工作项

```bash
# 注意：命令必须写在一行，不能有换行符
ones filter-issues --project <project_id> --sprint current --fields "title,status,description" --limit 20

# 按时间范围（含需求类型）
ones filter-issues --project <project_id> --updated-after "2026-01-01" --fields "title,status,priority,description" --type REQUIREMENT --limit 30

# 查询 Bug
ones filter-issues --project <project_id> --type BUG --status open --fields "title,description" --limit 20
```

### 3.2 常见 ONES 字段

| 字段 | 含义 | 可信度 |
|------|------|--------|
| `title` | 工作项标题 | L2 |
| `status` | 状态（开发中/测试中/已完成）| L2 |
| `description` | 详细描述 | L2 |
| `priority` | 优先级 | L2 |
| `assignee` | 负责人 | L2 |

### 3.3 避坑

- **命令不能有换行**：`ones filter-issues` 参数链不能跨行，会报解析错误
- **project_id 获取**：从 ONES URL `ones.sankuai.com/project/<id>` 提取
- **ONES 内容可信度**：ONES 描述为 L2，写入文档时不得当作 L1 事实，需代码验证

---

## 4. 代码文件批量读取策略

### 4.1 按模块分批（推荐）

每批 3-5 个文件，避免 context 溢出：

```
批次 1：BaseService + DataService（基础框架）→ L1
批次 2：SearchService + DetailService（高频核心模块）→ L1
批次 3：OrderService + PayService + ReserveService（交易链路）→ L1
批次 4：其余 Service（每批 3-4 个）→ L1
```

### 4.2 文件读取优先级

```
优先级 1：*Service.java（入口点，方法签名）
优先级 2：*/params/*Param.java（请求参数结构）
优先级 3：*/model/*Model.java（重要/复用频率高的）
优先级 4：util/*.java（工具类，按需）
```

### 4.3 从 Service 文件提取的关键信息

阅读每个 Service 文件时，提取：
- 类名、继承关系
- 每个 `public` 方法的签名（参数类型、返回类型）
- URL 字符串（`"mapchannel/..."` 形式）
- 是否有 `Lifecycle` 参数（无则记录到 implicit-knowledge）
- 特殊注释/TODO

---

## 5. 冲突处理策略（新增）

### 5.1 代码 vs 文档冲突

优先级：**代码（L1）> 学城文档（L2）> ONES（L2）**

处理方式：
```markdown
# 示例：文档说方法有 3 个参数，代码实际有 4 个

## API 端点列表

| 方法名 | 参数 | 说明 |
|--------|------|------|
| `requestXxx(key, owner, param, cb)` | 4个参数 | 见代码 XxxService.java:32 [L1] |

> [⚠️ 可能过时，以代码为准] 学城文档（ID:xxxx）显示参数为3个，
> 代码实际为4个（含 reqTimestamp），以代码为准。
```

### 5.2 多文档冲突

当两份学城文档描述同一接口不一致时：

```markdown
## XXX 接口参数

来源 A（学城文档 2731851958，L2）：参数包含 `foo`、`bar`
来源 B（学城文档 2758014734，L2）：参数包含 `foo`、`baz`

[待确认] 两份文档描述不一致，请确认以哪份为准，或以代码为准。
代码路径：`module/XxxService.java`（当前代码使用 `foo` + `bar`）
```

### 5.3 不确定内容处理

```markdown
# 场景：文档提到某功能但代码中未找到

[待确认] 学城文档提及 `requestXxxDetail` 方法，但代码中未找到该方法。
可能已删除或文档过时。请确认：(A) 该方法已废弃 (B) 在其他文件中
```

---

## 6. 模块文档生成优先级决策树

```
Service 文件数 > 10？
  ├── 是 → 按模块分组，每组出一个 module-details/*.md（单一原子化）
  └── 否 → 合并到 service-api-index.md 即可

模块有复杂 Model 层级？
  ├── 是 → module-details 中添加「关键字段索引」章节（含 JSON key → 类 → 文件路径）
  └── 否 → 简要列出即可

有多个版本差异字段？
  └── 是 → implicit-knowledge.md 中记录版本兼容性，标注 [待确认]
```

---

## 7. 增量更新知识库

当仓库新增文件/模块时：

1. 扫描新文件：`find src/ -newer docs/README.md -name "*.java"`
2. 读取新增文件，提取信息，标注 `confidence: L1`
3. 更新 `service-api-index.md`（追加行）
4. 更新 `file-index.md`（追加行）
5. 更新 `quick-lookup.md`（新业务场景）
6. **同步更新 `docs/README.md` 目录**（最常遗漏！）
7. 更新 README 中的「可检索信息范围」表格（文件数量变化）
8. 如有新已知坑，追加到 `implicit-knowledge.md`

---

## 8. 知识库质量验收标准（v2.0）

| 检查项 | 通过条件 | 关联规范 |
|--------|---------|---------|
| Service 覆盖率 | `service-api-index.md` 行数 ≥ Service 文件数 | 找的全 |
| 文件索引完整性 | `file-index.md` 文件数 ≥ 实际 .java 数 × 90% | 找的全 |
| 已知坑数量 | `implicit-knowledge.md` ≥ 5 条特殊设计 | 给的准 |
| README 同步 | 每个 docs/ 文件都在 README.md 中有条目 | 用的省 |
| 可检索范围声明 | README.md 含信息源访问状态表格 | 找的全 |
| AGENTS.md 路径 | P0 文档路径全部可 `cat` 验证存在 | 用的省 |
| frontmatter 覆盖率 | ≥90% docs/ 文件有完整 frontmatter | 用的省 |
| 冲突标注 | 有冲突的地方标注 `[⚠️ 可能过时]` 或 `[待确认]` | 给的准 |
| 无空文档 | 每个 .md 文件 ≥ 100 字 | 给的准 |
| 术语表完整性 | quick-lookup.md 术语表 ≥ 10 条 | 用的省 |

---

## 9. 实战案例（data-service 建库记录）

### 规模
- 27 个 Service 文件
- 51 个 API 端点
- 学城文档 8 篇（含架构图、API 约定、模块详情）
- ONES 工作项 20+ 条（2026 Q1-Q2）

### 耗时分布（参考）
- 阶段 0/0.5（工具检查 + 信息范围确认）：5 分钟
- 阶段 1（结构探索）：5 分钟
- 阶段 2（信息收集）：40 分钟（最耗时，27 个 Service 分 7 批读）
- 阶段 3（文档生成）：30 分钟
- 阶段 4（AGENTS.md）：10 分钟
- 阶段 5（校验）：5 分钟
- **总计：约 95 分钟**

### 最终产物
```
docs/
├── README.md                        # 含可检索范围表格
├── project-overview.md
├── architecture.md
├── service-api-index.md
├── api-protocol.md
├── quick-lookup.md                  # 含术语表
├── terminology.md
├── file-index.md
├── implicit-knowledge.md
├── ones-requirements-2026.md
└── module-details/
    ├── detail-module.md
    ├── order-module.md
    ├── search-module.md
    ├── favorite-module.md
    ├── board-module.md
    ├── login-auth-module.md
    └── pay-order-flow.md
AGENTS.md                            # 含信息可信度分级
```

### 踩过的坑

1. **Node 14 报错**：`oa-skills citadel` 需要 Node ≥18，先 `nvm use 18`
2. **ONES 命令换行报错**：`ones filter-issues` 所有参数必须在一行
3. **学城大文档 token 超限**：用 `head -200` 截断，聚焦核心章节
4. **marchantdata 目录名**：历史遗留拼写错误，绝对不能修改
5. **README.md 目录遗漏**：新增 module-details/ 后忘记更新 README
6. **文档与代码冲突未标注**：`CommentService` 文档提到 `requestCommentDetail`，代码已删除，需标注 `[⚠️ 可能过时]`
