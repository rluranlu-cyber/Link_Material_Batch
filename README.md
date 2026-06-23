# Batch Link Material | 批量链接材质

---

# 中文

> Blender 5.0.1 插件 · 单文件 · 中英双语

把任意数量的「父网格体」材质一键链接到对应的「子网格体」上，等价于 Blender 原生的 `Ctrl+L → Link Materials`，但支持**多组一一对应**一次执行，省去重复操作。

---

## 功能

- **左右一一对应**：每组关系指定一个子网格体（左，接收材质）和一个父网格体（右，提供材质）。
- **数量自定义**：
  - 0 组时点 `+` → **总数模式**，输入几就是几组。
  - 已有对应时点 `+` → **增量模式**，输入几就新增几组。
- **逐行删除**：每组对应关系右上角 `×` 按钮单独删除。
- **一键清空**：顶部 `🗑` 按钮清除所有对应关系（不动已建立的材质 link）。
- **执行后自动清零**：点 `Link Material` 完成链接后，面板自动回到 0 组干净状态，开始下一轮配置。已 link 的材质不受影响。
- **空对应自动跳过**：未填全 / 自指 / 非网格体的对应会被跳过，状态栏提示跳过数量。
- **网格体选择两种方式**：
  - 下拉搜索（仅列 MESH，可输入过滤）
  - 视口选中后点吸管按钮从活动对象拾取
- **中英双语**：根据 Blender 界面语言自动适配，无需配置。

---

## 安装

1. Blender → `编辑 > 设置 > 插件`（Edit > Preferences > Add-ons）。
2. 右上角下拉 → `从磁盘安装`（Install from Disk...）。
3. 选择 `link_material_batch.py`。
4. 勾选启用 **Batch Link Material**。

更新版本：先取消勾选旧版 → 重复上述安装步骤装新版。

---

## 使用

### 1. 打开面板

3D 视图按 `N` 打开侧边栏 → 切到 **LinkMat** 标签页。

### 2. 设置对应数量

| 当前状态 | 点 `+` 后 | 输入含义 |
|---------|---------|---------|
| 0 组（初始 / 执行后） | 总数模式 | 输入几就是几组 |
| >0 组（配置中途追加） | 增量模式 | 输入几就新增几组 |

### 3. 填写对应关系

每组关系两行：

- **左·子**：接收材质的网格体（材质会被覆盖）
- **右·父**：提供材质的网格体（材质数据源）

填写方式二选一：
- 下拉框直接搜索选择
- 视口里选中目标网格体使其成为活动对象，点吸管按钮拾取

### 4. 执行

点底部 `Link Material` 按钮：
- 子网格体材质槽被清空，引用父网格体的材质数据块（与 `Ctrl+L → Link Materials` 行为一致）。
- 状态栏提示「已链接 N 组材质，跳过 M 组未填/无效对应」。
- 面板自动清零，准备下一轮。

---

## 面板布局

```
┌─ Batch Link Material ─────────────┐
│ 对应数量: 3      [+] [🗑]          │
├──────────────────────────────────┤
│ ┌ 对应 1                  [×] ┐  │
│ │ 左·子  [下拉/搜索] [💉]      │  │
│ │ 右·父  [下拉/搜索] [💉]      │  │
│ └────────────────────────────┘  │
│ ┌ 对应 2                  [×] ┐  │
│ │ ...                          │  │
│ └────────────────────────────┘  │
├──────────────────────────────────┤
│       [  Link Material  ]        │
└──────────────────────────────────┘
```

---

## 操作流程示例

场景：3 个零件（Cube_A / Cube_B / Cube_C）需要分别继承 3 个高模（Hi_A / Hi_B / Hi_C）的材质。

1. 点 `+` → 输入 `3` → 确认，展开 3 组对应。
2. 第 1 组：左选 Cube_A，右选 Hi_A。
3. 第 2 组：左选 Cube_B，右选 Hi_B。
4. 第 3 组：左选 Cube_C，右选 Hi_C。
5. 点 `Link Material` → 3 组材质一次链接完成，面板清零。

---

## 行为说明

| 操作 | 影响面板配置 | 影响网格体材质 |
|------|:----------:|:------------:|
| 点 `+` 添加对应 | ✅ | ❌ |
| 点 `×` 删除单组 | ✅ | ❌ |
| 点 `🗑` 清空所有 | ✅ | ❌ |
| 点 `Link Material` | ✅（自动清零） | ✅（链接材质） |

**Link Material 的具体行为**：清空子网格体材质槽 → 逐个 append 父网格体的材质数据块。结果：子的材质槽与父完全一致，且指向相同 Material（修改父材质会同步影响子，与原生链接行为一致）。

---

## 多语言

| Blender 界面语言 | 面板显示 |
|----------------|---------|
| Simplified Chinese（简体中文） | 中文 |
| Default (English) / 其他语言 | 英文 |

切换路径：`编辑 > 设置 > 界面 > 翻译`，切换后即时生效，无需重启。

---

## 技术规格

| 项 | 值 |
|---|---|
| 兼容版本 | Blender 5.0.1 |
| 文件类型 | 单文件插件（`link_material_batch.py`） |
| 面板位置 | View3D > Sidebar (N) > LinkMat |
| 类别 | Material |
| 翻译域 | `link_material_batch` |
| 支持撤销 | ✅（UNDO） |

---

## 已知限制

- 仅支持网格体（MESH），其他类型（曲线、文本、骨架等）不列入下拉。
- 父子不能为同一对象（自指会被跳过）。
- 执行后无法通过单次 Undo 同时撤销「链接材质」和「面板清零」——它们是两个独立操作步骤，需按两次 `Ctrl+Z` 才能完全回到执行前状态（材质 link 撤销 + 面板对应恢复）。

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| 1.0.0 | 2026-06-22 | 初始版本：左右对应、`+` 设总数、Link Material 执行、空对应跳过 |
| 1.1.0 | 2026-06-22 | 智能模式（0组=总数 / >0组=增量）、逐行删除、简化状态管理 |
| 1.2.0 | 2026-06-23 | 中英双语 I18N 支持 |
| 1.2.1 | 2026-06-23 | 新增一键清空按钮；修复翻译表字典格式导致全部不翻译的 bug |

---

## 反馈

发现问题或有功能建议，直接反馈即可。

---
---

# English

> Blender 5.0.1 add-on · Single file · Chinese/English bilingual

One-click link of materials from any number of "parent meshes" to corresponding "child meshes" — equivalent to Blender's native `Ctrl+L → Link Materials`, but supports **multiple one-to-one pairs in a single execution**, eliminating repetitive operations.

---

## Features

- **One-to-one pairing**: Each pair specifies a child mesh (left, receives material) and a parent mesh (right, provides material).
- **Customizable count**:
  - At 0 pairs, clicking `+` → **Total mode** (input = total count).
  - With existing pairs, clicking `+` → **Increment mode** (input = added count).
- **Per-row delete**: `×` button at the top-right of each pair removes that single row.
- **Clear all**: `🗑` button at the top clears all pairs (does not affect established material links).
- **Auto-clear after execution**: After `Link Material` completes, the panel returns to 0 pairs for the next round. Established material links are unaffected.
- **Skip invalid pairs**: Unfilled / self-referential / non-mesh pairs are skipped, with skipped count shown in the status bar.
- **Two mesh selection methods**:
  - Dropdown search (lists MESH only, supports filtering)
  - Eyedropper button to pick from the active object after selecting it in the viewport
- **Bilingual (CN/EN)**: Auto-adapts to Blender's interface language, no configuration needed.

---

## Installation

1. Blender → `Edit > Preferences > Add-ons`.
2. Top-right dropdown → `Install from Disk...`.
3. Select `link_material_batch.py`.
4. Enable **Batch Link Material** by checking the box.

Updating: Uncheck the old version → repeat the install steps above for the new version.

---

## Usage

### 1. Open the panel

In the 3D viewport, press `N` to open the sidebar → switch to the **LinkMat** tab.

### 2. Set pair count

| Current state | After clicking `+` | Input meaning |
|---------|---------|---------|
| 0 pairs (initial / after execution) | Total mode | Input = total count |
| >0 pairs (adding during config) | Increment mode | Input = added count |

### 3. Fill in pairs

Each pair has two rows:

- **Left · Child**: Mesh that receives material (its materials will be overwritten)
- **Right · Parent**: Mesh that provides material (material source)

Two ways to fill:
- Search and select directly from the dropdown
- Select the target mesh in the viewport to make it active, then click the eyedropper button

### 4. Execute

Click the `Link Material` button at the bottom:
- Child mesh's material slots are cleared, then parent mesh's material data blocks are referenced (same behavior as `Ctrl+L → Link Materials`).
- Status bar shows "Linked N material(s), skipped M invalid/empty pair(s)".
- Panel auto-clears to 0, ready for the next round.

---

## Panel Layout

```
┌─ Batch Link Material ─────────────┐
│ Pair count: 3      [+] [🗑]        │
├──────────────────────────────────┤
│ ┌ Pair 1                   [×] ┐  │
│ │ L·Child  [dropdown] [💉]     │  │
│ │ R·Parent [dropdown] [💉]     │  │
│ └────────────────────────────┘  │
│ ┌ Pair 2                   [×] ┐  │
│ │ ...                          │  │
│ └────────────────────────────┘  │
├──────────────────────────────────┤
│       [  Link Material  ]        │
└──────────────────────────────────┘
```

---

## Workflow Example

Scenario: 3 parts (Cube_A / Cube_B / Cube_C) need to inherit materials from 3 high-poly meshes (Hi_A / Hi_B / Hi_C).

1. Click `+` → enter `3` → confirm. 3 pairs expand.
2. Pair 1: left = Cube_A, right = Hi_A.
3. Pair 2: left = Cube_B, right = Hi_B.
4. Pair 3: left = Cube_C, right = Hi_C.
5. Click `Link Material` → all 3 pairs linked in one go, panel clears.

---

## Behavior Matrix

| Operation | Affects panel config | Affects mesh material |
|------|:----------:|:------------:|
| Click `+` to add pairs | ✅ | ❌ |
| Click `×` to delete a pair | ✅ | ❌ |
| Click `🗑` to clear all | ✅ | ❌ |
| Click `Link Material` | ✅ (auto-clears) | ✅ (links material) |

**Link Material specific behavior**: Clears the child mesh's material slots → appends the parent mesh's material data blocks one by one. Result: child's material slots match the parent exactly, and point to the same Material data blocks (editing the parent material also affects the child, identical to native link behavior).

---

## Localization

| Blender interface language | Panel display |
|----------------|---------|
| Simplified Chinese | Chinese |
| Default (English) / others | English |

Switch path: `Edit > Preferences > Interface > Translation`. Changes take effect immediately without restart.

---

## Technical Specs

| Item | Value |
|---|---|
| Compatible version | Blender 5.0.1 |
| File type | Single-file add-on (`link_material_batch.py`) |
| Panel location | View3D > Sidebar (N) > LinkMat |
| Category | Material |
| Translation domain | `link_material_batch` |
| Undo support | ✅ (UNDO) |

---

## Known Limitations

- Only supports meshes (MESH). Other types (curves, text, armatures, etc.) are not listed in the dropdown.
- Parent and child cannot be the same object (self-reference is skipped).
- After execution, a single Undo cannot simultaneously undo "link material" and "panel clear" — they are two independent steps; press `Ctrl+Z` twice to fully return to the pre-execution state (undo material link + restore panel pairs).

---

## Version History

| Version | Date | Changes |
|------|------|---------|
| 1.0.0 | 2026-06-22 | Initial: left/right pairs, `+` for total count, Link Material execution, skip empty pairs |
| 1.1.0 | 2026-06-22 | Smart mode (0=total / >0=increment), per-row delete, simplified state management |
| 1.2.0 | 2026-06-23 | Chinese/English bilingual I18N |
| 1.2.1 | 2026-06-23 | Added clear-all button; fixed translation dict format bug causing no translation |

---

## Feedback

For issues or feature suggestions, just report directly.
