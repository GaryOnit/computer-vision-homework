# 知识库文档模板

每个模板对应 docs/ 目录下一个标准文档。复制模板，填入仓库实际内容。

## 通用规则

**文件名规范**：英文小写 + 连字符（`order-module.md`，非 `OrderModule.md`）

**frontmatter 字段说明**：
| 字段 | 说明 | 可选值 |
|------|------|--------|
| `topic` | 本文件一句话主题 | 任意字符串 |
| `keywords` | 同义词/别名/缩写/英文名（用于 AI 语义匹配） | 字符串数组 |
| `triggers` | 哪类问题/场景会用到本文件 | 字符串数组 |
| `confidence` | 知识可信度 | `L1`（代码/接口定义）\| `L2`（需求/设计文档）\| `L3`（变更历史/非正式） |
| `source` | 来源（代码文件路径 / 学城 URL / ONES ID） | 字符串 |
| `updated` | 最后更新日期 | `YYYY-MM-DD` |

**知识树层级**：
```
顶层（项目概述、架构全图、核心术语表）
  └── P0: README.md / service-api-index.md / quick-lookup.md / architecture.md

中层（模块/子系统说明、关键流程）
  └── P1/P2: implicit-knowledge.md / file-index.md / api-protocol.md / terminology.md / ones-requirements.md

底层（具体实现细节、文件索引、FAQ）
  └── P3: module-details/*.md
```

**冲突标注约定**：
- 代码 vs 文档冲突 → 以代码为准，文档标注 `[⚠️ 可能过时，以代码为准]`
- 多文档冲突 → 保留所有版本，标注来源，添加 `[待确认]`
- 不确定内容 → 标注 `[待确认]`，绝不编造

---

## T1: docs/README.md

```markdown
---
topic: <仓库名> 知识库索引与可检索范围声明
keywords: [知识库, 索引, 文档目录, AI 配置]
triggers: [AI 编码前加载, 查找文档位置, 了解知识库结构]
confidence: L1
source: docs/README.md
updated: YYYY-MM-DD
---

# <仓库名> 知识库

> AI 编码助手优先阅读本目录

## 可检索信息范围

| 信息源 | 可信度 | 状态 | 备注 |
|--------|--------|------|------|
| 代码库（src/） | L1（高，事实基准） | ✅ 已扫描 | 全量 <N> 个 .java 文件 |
| ONES 项目 <id> | L2（中，上下文参考） | ✅ 已读取 / ❌ 无法访问 | <备注> |
| 学城文档 <id> | L2（中，设计参考） | ✅ 已读取 / ❌ 无法访问 | <备注> |

> 无法访问的资源已在构建时列清单确认。

## 知识树结构

### 顶层（项目概述 / 架构全图 / 核心术语）
#### P0（必读 — AI 每次编码前载入）
- `docs/service-api-index.md` — Service↔API 端点全量映射 [L1]
- `docs/quick-lookup.md` — 业务场景→文件路径速查 + 术语表 [L1]

#### P0/P1（结构理解）
- `docs/architecture.md` — 类层级、请求流程 [L1]

### 中层（模块说明 / 关键流程）
#### P1（按需 — 涉及对应模块时载入）
- `docs/file-index.md` — 全量文件路径索引 [L1]
- `docs/implicit-knowledge.md` — 已知坑、特殊设计 [L1]

#### P2（背景参考）
- `docs/api-protocol.md` — 网络协议、请求头 [L2]
- `docs/terminology.md` — 专有名词释义 [L1/L2]
- `docs/ones-requirements-<year>.md` — 需求背景 [L2]

### 底层（实现细节 / 文件索引）
#### P3（模块深度）
- `docs/module-details/<module>.md` — 核心模块文档 [L1]

## 外部链接
- 学城文档：<km_url>
- ONES 项目：<ones_url>
- 代码仓库：<repo_url>
```

---

## T2: docs/service-api-index.md

```markdown
---
topic: <仓库名> 全量 Service 接口与 API 端点映射表
keywords: [Service, API, 端点, 接口, mapchannel, 方法签名]
triggers: [找哪个 Service 负责 XX 功能, 查 API 端点对应的方法, 接口在哪个文件]
confidence: L1
source: data-service/src/main/java/...（代码直接提取）
updated: YYYY-MM-DD
---

# Service ↔ API 端点索引

> 共 N 个 Service，M 个 API 端点。来源：代码直读，可信度 L1。

## 按 Service 分组

### XxxService (`module/XxxService.java`)
| 方法名 | API 端点 | Param | 返回 Model | 特殊说明 |
|--------|---------|-------|-----------|---------|
| `requestXxx(key, owner, param, cb)` | `mapchannel/xxx_endpoint` | `XxxParam` | `XxxModel` | — |

## 按 API 端点检索

| API 端点 | Service 文件 | 方法名 |
|---------|-------------|--------|
| `mapchannel/xxx_endpoint` | `module/XxxService.java` | `requestXxx` |
```

---

## T3: docs/quick-lookup.md

```markdown
---
topic: 业务场景到代码文件的快速定位索引
keywords: [快速查找, 场景定位, 术语反查, 文件路径, 业务词汇]
triggers: [XXX 功能在哪个文件, 我要做 XX 场景, 这个术语对应哪个类]
confidence: L1
source: data-service/src/main/java/...（代码直读）
updated: YYYY-MM-DD
---

# 快速定位索引

## 按业务场景

| 用户说... | 对应文件 | 核心方法 |
|----------|---------|---------|
| "POI 详情/商户详情" | `detail/DetailService.java` | `requestPoiDetail` |
| "搜索/找地方" | `search/SearchService.java` | `requestSearchList` |
| ...（覆盖全部核心业务场景）| | |

## 按模块速查

| 模块 | 目录 | Service 文件 | confidence |
|------|------|-------------|-----------|
| 详情 | `detail/` | `DetailService.java` | L1 |
| ...  | ...  | ... | ... |

## 核心术语表（术语 → 解释 + 代码定位）

| 术语 | 解释 | 代码文件 |
|------|------|---------|
| `DayNightDTO` | 白天/夜间模式数据结构 | `reserve/model/DayNightDTO.java` |
| `SafeArea` | 安全区域坐标描述，需特殊序列化 | `base/SafeArea.java` |
| ...  | ... | ... |
```

---

## T4: docs/architecture.md

```markdown
---
topic: <仓库名> 技术架构与请求流程
keywords: [架构, 类层级, 请求流程, BaseService, StarShip, 依赖关系]
triggers: [架构是什么样的, 请求怎么发出去的, Service 继承关系, 各层职责]
confidence: L1
source: data-service/src/main/java/.../base/（代码直读）
updated: YYYY-MM-DD
---

# 技术架构

## 类层级

\`\`\`
DataService（入口单例）
  └── XxxService extends BaseService
        └── 使用 StarShip/OkHttp 发起请求
              └── 回调 IServiceResultV2<T>
\`\`\`

## 请求流程

1. 调用方创建 `XxxParam` → 调用 `XxxService.requestXxx(key, owner, param, callback)`
2. BaseService 拼接 Header（mtm-signature、X-INFO、platinfo）
3. StarShip 发起 HTTP POST → `ServiceConstants.getBaseUrl() + "/mapchannel/xxx"`
4. 响应反序列化为 `XxxModel`，回调 `onSuccess(model, headers, displayData, msg, extra)` 或 `onFailure(httpCode, serverCode, e, ...)`

## 关键类

| 类名 | 职责 | 文件路径 |
|------|------|---------|
| `DataService` | 入口单例，初始化所有 Service | `base/DataService.java` |
| `BaseService` | 公共请求逻辑，Header 注入 | `base/BaseService.java` |
| `IServiceResultV2<T>` | 回调接口（7参数） | `common/IServiceResultV2.java` |
| `ServiceConstants` | URL、状态码常量 | `common/ServiceConstants.java` |

## Lifecycle 绑定

绝大多数 Service 方法签名为：
\`\`\`java
requestXxx(String key, Lifecycle owner, XxxParam param, IServiceResultV2<XxxModel> callback)
\`\`\`
⚠️ 例外：`GuardService.requestGuardInfo` 无 Lifecycle 参数。
```

---

## T5: docs/implicit-knowledge.md

```markdown
---
topic: 已知特殊设计、历史遗留约束与反直觉行为速查
keywords: [已知坑, 特殊设计, 历史遗留, 反直觉, 注意事项, 陷阱]
triggers: [为什么这样设计, 这个方法签名对吗, 有没有特殊情况, 踩坑]
confidence: L1
source: data-service/src/main/java/...（代码直读）+ 开发者经验
updated: YYYY-MM-DD
---

# 隐性知识与已知坑

> AI 编码时必须对照本文件，防止踩坑

## 已知特殊设计（不可修改项）

| 涉及对象 | 特殊行为 | 正确处理方式 | 代码来源（L1）|
|---------|---------|------------|------------|
| `marchantdata/` | 目录名拼写错误（非 merchantdata），历史遗留 | NEVER 修改此目录名 | 目录结构 |
| `GuardService` | `requestGuardInfo` 无 Lifecycle 参数 | 直接传 param + callback | `guard/GuardService.java` |
| `operateFavorite` | null result 走 `onSuccess(false)` | 在 onSuccess 检查 result != null | `favorite/FavoriteService.java` |
| `LoginService` | `requestLoginStatus` 包级私有 | 通过 DataService 调用 | `login/LoginService.java` |
| `SafeArea`字段 | 需注册 `SafeAreaSerializer` | 初始化时显式注册 | `base/SafeAreaSerializer.java` |

## 设计决策记录

### 为什么 XXX 这样设计？
- 背景：...
- 约束：...
- 结论：...

## 文档与代码冲突记录

| 冲突点 | 文档说 | 代码实际 | 处理方式 |
|--------|--------|---------|---------|
| XXX 方法参数 | [⚠️ 可能过时，以代码为准] | ... | 以代码为准 |

## 待确认项

- [ ] [待确认] XXX 字段在低版本的行为（来源：学城文档，未有代码验证）
```

---

## T6: docs/module-details/`<module-name>`.md

> **单一原子化**：每个文件只描述一个模块/概念。文件名语义化英文小写。

```markdown
---
topic: <模块名>模块接口与字段索引
keywords: [模块名, 相关业务场景词, 英文名, 缩写]
triggers: [XX 功能怎么实现, XX 接口参数是什么, XX 字段在哪个类]
confidence: L1
source: <module>/XxxService.java + <module>/model/ + <module>/params/
updated: YYYY-MM-DD
---

# <模块名>模块

## 功能范围
<一句话描述，不超过30字>

## Service 文件
- 主 Service：`<module>/<ModuleName>Service.java`
- 关联 Model：`<module>/model/` 下全部文件
- 关联 Param：`<module>/params/` 下全部文件

## API 端点列表（L1 — 代码直读）

| 方法名 | 端点 | Param | 返回 Model | 特殊说明 |
|--------|------|-------|-----------|---------|
| `requestXxx` | `mapchannel/xxx` | `XxxParam` | `XxxModel` | — |

## 关键字段索引（L1）

| 字段名（Java）| JSON key | 类型 | 所在类 | 说明 |
|-------------|---------|------|--------|------|
| `fieldName` | `"json_key"` | `String` | `XxxModel` | 描述 |

## 已知注意事项
- ⚠️ 特殊行为 1（来源：代码，L1）
- ⚠️ [⚠️ 可能过时，以代码为准] 文档中提到的 XXX（来源：学城文档，L2）

## ONES 需求关联（L2）
- ONES#xxx — 功能描述
```

---

## T7: AGENTS.md

```markdown
# AGENTS.md — <仓库名> AI 助手配置

## 信息可信度分级

| 来源 | 可信度 | 优先级 |
|------|--------|-------|
| 本仓库代码（.java文件） | L1（最高，客观事实） | 首选 |
| 本知识库（docs/） | L1/L2（来自代码+文档提取） | 次选 |
| ONES 需求/任务/Bug | L2（中） | 功能背景参考 |
| 学城技术文档 | L2（中） | 设计方案参考 |

> ⚠️ 文档与代码冲突时，以代码为准。文档中标注 `[⚠️ 可能过时]` 的内容需先查代码确认。

## 知识库路径

### P0（每次编码前必读，L1）
- `docs/service-api-index.md` — Service↔API 端点全量映射
- `docs/quick-lookup.md` — 业务场景→文件+术语表

### P1（涉及对应模块时读）
- `docs/architecture.md` — 类层级、请求流程 [L1]
- `docs/file-index.md` — 全量文件路径索引 [L1]
- `docs/implicit-knowledge.md` — 已知坑、特殊设计 [L1]

### P2（背景参考）
- `docs/api-protocol.md` — 网络协议、请求头 [L2]
- `docs/terminology.md` — 专有名词释义 [L1/L2]
- `docs/ones-requirements-<year>.md` — 需求背景 [L2]

### P3（模块深度）
- `docs/module-details/*.md` — 核心模块文档 [L1]

## 已知坑速查（高频，L1）

| 场景 | 必查注意事项 |
|------|------------|
| marchantdata 目录 | ⚠️ 拼写错误，不得修改 |
| GuardService | ⚠️ 无 Lifecycle 参数 |
| （...补充5-8条）| |

## 编码约束

- 新 Service 必须继承 `BaseService`
- 回调统一使用 `IServiceResultV2<T>`（7参数，非旧版3参数）
- 不得直接使用 OkHttp，通过 StarShip 封装
- URL 必须通过 `ServiceConstants.getBaseUrl()` 构建

## 环境依赖

- Node ≥18（运行 citadel/ONES CLI 需要 `nvm use 18`）
```
