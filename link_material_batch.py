bl_info = {
    "name": "Batch Link Material",
    "author": "WorkBuddy",
    "version": (1, 1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar (N) > LinkMat",
    "description": "批量将父网格体的材质链接到子网格体（左右一一对应，数量可自定义，支持逐行删除）",
    "category": "Material",
}

import bpy
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    IntProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup, Operator, Panel


# ---------------------------------------------------------------------------
# 属性组：一组对应关系（左·子网格体 / 右·父网格体）
# ---------------------------------------------------------------------------

def _mesh_poll(self, obj):
    """PointerProperty 过滤器：下拉列表里只显示网格体（MESH）。"""
    return obj.type == 'MESH'


class LinkMatPair(PropertyGroup):
    child_obj: PointerProperty(
        name="子网格体",
        description="左侧 · 接收材质的子网格体",
        type=bpy.types.Object,
        poll=_mesh_poll,
    )
    parent_obj: PointerProperty(
        name="父网格体",
        description="右侧 · 提供材质的父网格体",
        type=bpy.types.Object,
        poll=_mesh_poll,
    )


# ---------------------------------------------------------------------------
# Operator：设置/增加对应数量（点击 "+"）
#   模式判断（无需额外标志位，纯按当前对应数推断）：
#     - 当前 0 组 → 总数模式：输入几就是几组（首次配置 / 执行完 Link 后重新开始）
#     - 当前 >0 组 → 增量模式：输入几就新增几组（配置中途追加）
#   两种模式 execute 逻辑都是“追加 N 组”，区别仅在对话框提示文案。
# ---------------------------------------------------------------------------

class LINKMAT_OT_set_count(Operator):
    bl_idname = "linkmat.set_count"
    bl_label = "对应数量"
    bl_description = "设置或增加对应关系数量（0 组时为总数模式，已有对应时为增量模式）"
    bl_options = {'REGISTER', 'UNDO'}

    count: IntProperty(
        name="数量",
        description="要设置或新增的对应关系数量",
        default=1, min=1, max=500,
    )

    def invoke(self, context, event):
        # 两种模式默认值都给 1，用户自行修改。
        self.count = 1
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        pairs = context.scene.linkmat_pairs
        if len(pairs) == 0:
            # 总数模式
            layout.label(text="设置对应关系总数", icon='INFO')
            layout.prop(self, "count", text="总数")
        else:
            # 增量模式
            layout.label(text=f"当前已有 {len(pairs)} 组，将在此基础上新增", icon='INFO')
            layout.prop(self, "count", text="新增数量")

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        # 两种模式都是追加 N 组。
        for _ in range(self.count):
            pairs.add()
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：删除指定对应关系（每行右上角的 X 按钮）
# ---------------------------------------------------------------------------

class LINKMAT_OT_delete_pair(Operator):
    bl_idname = "linkmat.delete_pair"
    bl_label = "删除此对应"
    bl_description = "删除这一组对应关系"
    bl_options = {'REGISTER', 'UNDO'}

    pair_index: IntProperty(default=0)

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        if self.pair_index < 0 or self.pair_index >= len(pairs):
            self.report({'ERROR'}, "对应关系索引无效")
            return {'CANCELLED'}
        pairs.remove(self.pair_index)
        # 全删光后，下次点 "+" 自动回到总数模式（因为 len==0）。
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：从当前活动对象拾取，填入指定字段（子 或 父）
# ---------------------------------------------------------------------------

class LINKMAT_OT_pick_active(Operator):
    bl_idname = "linkmat.pick_active"
    bl_label = "从活动对象拾取"
    bl_description = "将当前活动（最后选中）的网格体填入此字段"
    bl_options = {'REGISTER', 'UNDO'}

    pair_index: IntProperty(default=0)
    field: EnumProperty(
        items=[
            ('CHILD', "子", "填入左侧子网格体"),
            ('PARENT', "父", "填入右侧父网格体"),
        ],
        default='CHILD',
    )

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "请先选中一个网格体作为活动对象")
            return {'CANCELLED'}
        pairs = context.scene.linkmat_pairs
        if self.pair_index < 0 or self.pair_index >= len(pairs):
            self.report({'ERROR'}, "对应关系索引无效")
            return {'CANCELLED'}
        pair = pairs[self.pair_index]
        if self.field == 'CHILD':
            pair.child_obj = obj
        else:
            pair.parent_obj = obj
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator：执行 Link Material（等价于 Ctrl+L → Link Materials）
# ---------------------------------------------------------------------------

class LINKMAT_OT_link_material(Operator):
    bl_idname = "linkmat.link_material"
    bl_label = "Link Material"
    bl_description = "将每个有效对应关系中父网格体的材质链接到子网格体，完成后清空面板回归 0 组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pairs = context.scene.linkmat_pairs
        if len(pairs) == 0:
            self.report({'WARNING'}, "没有对应关系，请先点 + 添加")
            return {'CANCELLED'}

        done = 0
        skipped = 0
        for pair in pairs:
            child = pair.child_obj
            parent = pair.parent_obj
            # 空对应 / 自指 / 类型不符 -> 跳过
            if child is None or parent is None:
                skipped += 1
                continue
            if child == parent:
                skipped += 1
                continue
            if child.type != 'MESH' or parent.type != 'MESH':
                skipped += 1
                continue

            # 复刻 Ctrl+L → Link Materials 的行为：
            # 清空子网格体的材质槽，再引用父网格体的同一批材质数据块。
            # 结果：子的材质槽与父完全一致，且指向相同的 Material 数据块。
            child.data.materials.clear()
            for mat in parent.data.materials:
                child.data.materials.append(mat)
            done += 1

        msg = f"已链接 {done} 组材质"
        if skipped:
            msg += f"，跳过 {skipped} 组未填/无效对应"
        self.report({'INFO'}, msg)

        # 执行完毕：清空所有对应关系，回归“0 组干净状态”。
        # 已建立的材质 link 关系不受影响（仅清空面板配置，不动网格体材质槽）。
        # 清空后 len==0，下次点 "+" 自动进入总数模式，开始新一轮配置。
        while len(pairs) > 0:
            pairs.remove(0)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Panel：N 侧边栏
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

        # 顶部：当前数量 + "+"按钮
        header = layout.row(align=True)
        header.label(text=f"对应数量: {len(pairs)}")
        header.operator("linkmat.set_count", text="", icon='ADD')

        layout.separator()

        if len(pairs) == 0:
            layout.label(text="暂无对应关系，点 + 添加", icon='INFO')
            return

        # 逐行绘制对应关系：左·子 / 右·父
        for i, pair in enumerate(pairs):
            box = layout.box()

            # 行头：左侧标题 + 右侧删除按钮
            head = box.row(align=True)
            head.label(text=f"对应 {i + 1}", icon='LINKED')
            head.alignment = 'RIGHT'
            op = head.operator("linkmat.delete_pair", text="", icon='X')
            op.pair_index = i

            # 左：子网格体（接收材质）
            row = box.row(align=True)
            row.label(text="左·子")
            row.prop(pair, "child_obj", text="")
            op = row.operator("linkmat.pick_active", text="", icon='EYEDROPPER')
            op.pair_index = i
            op.field = 'CHILD'

            # 右：父网格体（提供材质）
            row = box.row(align=True)
            row.label(text="右·父")
            row.prop(pair, "parent_obj", text="")
            op = row.operator("linkmat.pick_active", text="", icon='EYEDROPPER')
            op.pair_index = i
            op.field = 'PARENT'

        layout.separator()

        # 执行按钮
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
    LINKMAT_OT_pick_active,
    LINKMAT_OT_link_material,
    LINKMAT_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.linkmat_pairs = CollectionProperty(type=LinkMatPair)
    # 不在 register() 里访问 bpy.data.scenes（安装阶段 _RestrictData 限制）。
    # 不做惰性初始化：面板初始即为 0 组，与执行 Link Material 后的干净状态一致，
    # 同时让 "+" 按钮的模式判断（0 组=总数 / >0 组=增量）自然成立。


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "linkmat_pairs"):
        del bpy.types.Scene.linkmat_pairs


if __name__ == "__main__":
    register()
