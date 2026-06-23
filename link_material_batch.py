bl_info = {
    "name": "Batch Link Material",
    "author": "WorkBuddy",
    "version": (1, 2, 1),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar (N) > LinkMat",
    "description": "Batch link parent mesh material to child mesh (one-to-one pairs, customizable count, per-row delete, clear all)",
    "category": "Material",
    "bl_translation": {"domain": "link_material_batch"},
}

import bpy
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    IntProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup, Operator, Panel

DOMAIN = "link_material_batch"

# ---------------------------------------------------------------------------
# I18N 翻译表（Blender 标准格式）
#   key:   (msgctxt, msgid)     —— msgctxt="*" 表示默认上下文
#   value: {lang_code: translation}
#
# msgid 统一用英文（Blender 默认/回退语言）。
# 仅提供 zh_HANS（简体中文）翻译；其他语言自动回退到英文 msgid。
# 当用户在 Preferences > Interface > Translation 选 Simplified Chinese 时，
# 所有 pgettext_iface / pgettext_tip 包装的字符串自动返回中文；
# 选其他语言或 Default (English) 时返回英文 msgid。
# ---------------------------------------------------------------------------

TRANSLATIONS = {
    "zh_HANS": {
        # ---- 类名 / 描述（bl_label / bl_description 自动翻译）----
        ("*", "Batch Link Material"): "批量链接材质",
        ("*", "Set pair count"): "设置对应数量",
        ("*", "Set or add pair count (0 pairs = total mode, >0 pairs = increment mode)"): "设置或增加对应关系数量（0 组时为总数模式，已有对应时为增量模式）",
        ("*", "Delete this pair"): "删除此对应",
        ("*", "Clear all pairs"): "清空所有对应关系",
        ("*", "Pick from active object"): "从活动对象拾取",
        ("*", "Link Material"): "Link Material",
        ("*", "Link each valid pair's parent material to child, then clear panel to 0 pairs"): "将每个有效对应关系中父网格体的材质链接到子网格体，完成后清空面板回归 0 组",
        ("*", "Child mesh (left, receives material)"): "子网格体（左侧 · 接收材质）",
        ("*", "Parent mesh (right, provides material)"): "父网格体（右侧 · 提供材质）",

        # ---- 面板顶部 ----
        ("*", "Pair count: %d"): "对应数量: %d",
        ("*", "No pairs yet, click + to add"): "暂无对应关系，点 + 添加",

        # ---- 单组对应关系 ----
        ("*", "Pair %d"): "对应 %d",
        ("*", "Left · Child"): "左·子",
        ("*", "Right · Parent"): "右·父",
        ("*", "Child"): "子",
        ("*", "Parent"): "父",

        # ---- 设置数量对话框 ----
        ("*", "Pair count"): "对应数量",
        ("*", "Count"): "数量",
        ("*", "Set total pair count"): "设置对应关系总数",
        ("*", "Total"): "总数",
        ("*", "Current: %d pairs, will add"): "当前已有 %d 组，将在此基础上新增",
        ("*", "Add amount"): "新增数量",

        # ---- 状态栏 / 错误提示 ----
        ("*", "Linked %d material(s)"): "已链接 %d 组材质",
        ("*", ", skipped %d invalid/empty pair(s)"): "，跳过 %d 组未填/无效对应",
        ("*", "Cleared %d pair(s)"): "已清空 %d 组对应关系",
        ("*", "No pairs, click + to add first"): "没有对应关系，请先点 + 添加",
        ("*", "Please select a mesh as active object first"): "请先选中一个网格体作为活动对象",
        ("*", "Invalid pair index"): "对应关系索引无效",

        # ---- 拾取按钮的 tooltip ----
        ("*", "Fill into left child mesh"): "填入左侧子网格体",
        ("*", "Fill into right parent mesh"): "填入右侧父网格体",
    },
}


def iface_(msg, *args):
    """界面文本翻译（label、按钮文字等）。"""
    text = bpy.app.translations.pgettext_iface(msg)
    if args:
        try:
            return text % args
        except Exception:
            return text
    return text


def tip_(msg, *args):
    """提示/状态栏文本翻译（self.report、tooltip 等）。"""
    text = bpy.app.translations.pgettext_tip(msg)
    if args:
        try:
            return text % args
        except Exception:
            return text
    return text


# ---------------------------------------------------------------------------
# 属性组
# ---------------------------------------------------------------------------

def _mesh_poll(self, obj):
    """PointerProperty 过滤器：下拉列表里只显示网格体（MESH）。"""
    return obj.type == 'MESH'


class LinkMatPair(PropertyGroup):
    child_obj: PointerProperty(
        name="Child mesh (left, receives material)",
        description="Child mesh (left, receives material)",
        type=bpy.types.Object,
        poll=_mesh_poll,
    )
    parent_obj: PointerProperty(
        name="Parent mesh (right, provides material)",
        description="Parent mesh (right, provides material)",
        type=bpy.types.Object,
        poll=_mesh_poll,
    )


# ---------------------------------------------------------------------------
# Operator：设置/增加对应数量（点击 "+"）
#   0 组 → 总数模式；>0 组 → 增量模式。两种模式 execute 都是"追加 N 组"。
# ---------------------------------------------------------------------------

class LINKMAT_OT_set_count(Operator):
    bl_idname = "linkmat.set_count"
    bl_label = "Set pair count"
    bl_description = "Set or add pair count (0 pairs = total mode, >0 pairs = increment mode)"
    bl_options = {'REGISTER', 'UNDO'}

    count: IntProperty(
        name="Count",
        description="Count",
        default=1, min=1, max=500,
    )

    def invoke(self, context, event):
        self.count = 1
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        pairs = context.scene.linkmat_pairs
        if len(pairs) == 0:
            layout.label(text=iface_("Set total pair count"), icon='INFO')
            layout.prop(self, "count", text=iface_("Total"))
        else:
            layout.label(text=iface_("Current: %d pairs, will add", len(pairs)), icon='INFO')
            layout.prop(self, "count", text=iface_("Add amount"))

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        for _ in range(self.count):
            pairs.add()
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：删除指定对应关系（每行右上角的 X 按钮）
# ---------------------------------------------------------------------------

class LINKMAT_OT_delete_pair(Operator):
    bl_idname = "linkmat.delete_pair"
    bl_label = "Delete this pair"
    bl_description = "Delete this pair"
    bl_options = {'REGISTER', 'UNDO'}

    pair_index: IntProperty(default=0)

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        if self.pair_index < 0 or self.pair_index >= len(pairs):
            self.report({'ERROR'}, tip_("Invalid pair index"))
            return {'CANCELLED'}
        pairs.remove(self.pair_index)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：一键清空所有对应关系（顶部 TRASH 按钮）
# ---------------------------------------------------------------------------

class LINKMAT_OT_clear_all(Operator):
    bl_idname = "linkmat.clear_all"
    bl_label = "Clear all pairs"
    bl_description = "Clear all pairs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        n = len(pairs)
        while len(pairs) > 0:
            pairs.remove(0)
        self.report({'INFO'}, tip_("Cleared %d pair(s)", n))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：从当前活动对象拾取
# ---------------------------------------------------------------------------

class LINKMAT_OT_pick_active(Operator):
    bl_idname = "linkmat.pick_active"
    bl_label = "Pick from active object"
    bl_description = "Pick from active object"
    bl_options = {'REGISTER', 'UNDO'}

    pair_index: IntProperty(default=0)
    field: EnumProperty(
        items=[
            ('CHILD', "Child", "Child"),
            ('PARENT', "Parent", "Parent"),
        ],
        default='CHILD',
    )

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, tip_("Please select a mesh as active object first"))
            return {'CANCELLED'}
        pairs = context.scene.linkmat_pairs
        if self.pair_index < 0 or self.pair_index >= len(pairs):
            self.report({'ERROR'}, tip_("Invalid pair index"))
            return {'CANCELLED'}
        pair = pairs[self.pair_index]
        if self.field == 'CHILD':
            pair.child_obj = obj
        else:
            pair.parent_obj = obj
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：执行 Link Material
# ---------------------------------------------------------------------------

class LINKMAT_OT_link_material(Operator):
    bl_idname = "linkmat.link_material"
    bl_label = "Link Material"
    bl_description = "Link each valid pair's parent material to child, then clear panel to 0 pairs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        if len(pairs) == 0:
            self.report({'WARNING'}, tip_("No pairs, click + to add first"))
            return {'CANCELLED'}

        done = 0
        skipped = 0
        for pair in pairs:
            child = pair.child_obj
            parent = pair.parent_obj
            if child is None or parent is None:
                skipped += 1
                continue
            if child == parent:
                skipped += 1
                continue
            if child.type != 'MESH' or parent.type != 'MESH':
                skipped += 1
                continue

            child.data.materials.clear()
            for mat in parent.data.materials:
                child.data.materials.append(mat)
            done += 1

        msg = tip_("Linked %d material(s)", done)
        if skipped:
            msg += tip_(", skipped %d invalid/empty pair(s)", skipped)
        self.report({'INFO'}, msg)

        while len(pairs) > 0:
            pairs.remove(0)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class LINKMAT_PT_panel(Panel):
    bl_label = "Batch Link Material"
    bl_idname = "LINKMAT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LinkMat"

    def draw(self, context):
        layout = self.layout
        pairs = context.scene.linkmat_pairs

        # 顶部：当前数量 + "+"按钮 + 清空按钮
        # 注意：layout.operator() 返回的是 operator 属性结构体，不是 UI 按钮，
        # 不能对它设 .enabled（会抛 AttributeError 导致整个 draw 中止，
        # 表现为顶部数字画出来了但下面的对应关系框全部消失）。
        # 改为：仅当有对应关系时才创建垃圾桶按钮。
        header = layout.row(align=True)
        header.label(text=iface_("Pair count: %d", len(pairs)))
        header.operator("linkmat.set_count", text="", icon='ADD')
        if len(pairs) > 0:
            header.operator("linkmat.clear_all", text="", icon='TRASH')

        layout.separator()

        if len(pairs) == 0:
            layout.label(text=iface_("No pairs yet, click + to add"), icon='INFO')
            return

        for i, pair in enumerate(pairs):
            box = layout.box()

            # 行头：标题 + 删除按钮
            head = box.row(align=True)
            head.label(text=iface_("Pair %d", i + 1), icon='LINKED')
            head.alignment = 'RIGHT'
            op = head.operator("linkmat.delete_pair", text="", icon='X')
            op.pair_index = i

            # 左：子网格体
            row = box.row(align=True)
            row.label(text=iface_("Left · Child"))
            row.prop(pair, "child_obj", text="")
            op = row.operator("linkmat.pick_active", text="", icon='EYEDROPPER')
            op.pair_index = i
            op.field = 'CHILD'

            # 右：父网格体
            row = box.row(align=True)
            row.label(text=iface_("Right · Parent"))
            row.prop(pair, "parent_obj", text="")
            op = row.operator("linkmat.pick_active", text="", icon='EYEDROPPER')
            op.pair_index = i
            op.field = 'PARENT'

        layout.separator()

        big = layout.row()
        big.scale_y = 1.6
        big.operator("linkmat.link_material", text="Link Material", icon='LINKED')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    LinkMatPair,
    LINKMAT_OT_set_count,
    LINKMAT_OT_delete_pair,
    LINKMAT_OT_clear_all,
    LINKMAT_OT_pick_active,
    LINKMAT_OT_link_material,
    LINKMAT_PT_panel,
)


def register():
    # 先注册翻译域，再注册类（类定义里的 bl_label 通过 default domain 查找，
    # default domain 已包含所有 register 过的翻译表）。
    bpy.app.translations.register(DOMAIN, TRANSLATIONS)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.linkmat_pairs = CollectionProperty(type=LinkMatPair)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "linkmat_pairs"):
        del bpy.types.Scene.linkmat_pairs
    if DOMAIN in bpy.app.translations.loaded_domains:
        bpy.app.translations.unregister(DOMAIN)


if __name__ == "__main__":
    register()
