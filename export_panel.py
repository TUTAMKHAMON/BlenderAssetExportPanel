bl_info = {
	"name": "Unity Export",
	"description": "A way to expedite the process of exporting multiple groups of objects into separate files.",
	"author": "João Ferreira (@TUTAMKHAMON)",
	"version": (1, 3),
	"blender": (2, 80, 0),
	"location": "View3D > Sidebar > Asset Exporter",
	"support": "COMMUNITY",
	"warning": "",  #TODO: if any major bug is detected, update with info
	"doc_url": "https://github.com/TUTAMKHAMON/BlenderAssetExportPanel",
	"category": "Import-Export",
}



import bpy


class ASSET_EXPORT_obj_list(bpy.types.PropertyGroup):
	obj: bpy.props.PointerProperty(type=bpy.types.Object)


class ASSET_EXPORT_entry(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name='Object name', default='Unnamed')
	export: bpy.props.BoolProperty(name='Export boolean', default=True)
	objs: bpy.props.CollectionProperty(type=ASSET_EXPORT_obj_list)


class ASSET_EXPORT_data(bpy.types.PropertyGroup):
	export_path: bpy.props.StringProperty(name='Export path', default='/')

	selected_rendered: bpy.props.IntProperty(name='Render export group')
	current_render_name: bpy.props.StringProperty(name='Render file name')
	rendered_objs: bpy.props.CollectionProperty(
		type=ASSET_EXPORT_entry,
		description='Unity Export: Rendered objects list')

	selected_collision: bpy.props.IntProperty(name='Collision export group')
	current_collision_name: bpy.props.StringProperty(name='Collision file name')
	collision_objs: bpy.props.CollectionProperty(
		type=ASSET_EXPORT_entry,
		description='Unity Export: Collision objects list')


class ASSET_EXPORT_Add_Export(bpy.types.Operator):
	bl_idname = 'tae.add_export'
	bl_label = ''
	bl_options = {'REGISTER'}

	export_name: bpy.props.StringProperty()
	list: bpy.props.StringProperty()

	@classmethod
	def description(cls, context, properties):
		return "Add objects to the " + properties.list + " export list"

	def execute(self, context):
		obj = context.object

		if self.list == 'render':
			collection = bpy.context.scene.asset_export.rendered_objs
			selected = bpy.context.scene.asset_export.selected_rendered
		elif self.list == 'collision':
			collection = bpy.context.scene.asset_export.collision_objs
			selected = bpy.context.scene.asset_export.selected_collision
		else:
			return {'CANCELLED'}

		newRO = collection.add()
		newRO.name = self.export_name

		for o in context.selected_objects:
			if o.type == 'MESH':
				go = newRO.objs.add()
				go.obj = o

		selected = collection.keys().__len__() - 1
		return {'FINISHED'}


class ASSET_EXPORT_Remove_Export(bpy.types.Operator):
	bl_idname = 'tae.remove_export'
	bl_label = ''
	bl_options = {'REGISTER'}

	del_index: bpy.props.IntProperty()
	list: bpy.props.StringProperty()

	@classmethod
	def description(self, context, properties):
		return "Remove selected object from the " + properties.list + " export list"

	def execute(self, context):

		if self.list == 'render':
			collection = bpy.context.scene.asset_export.rendered_objs
		elif self.list == 'collision':
			collection = bpy.context.scene.asset_export.collision_objs
		else:
			return {'CANCELLED'}

		collection.remove(self.del_index)
		return {'FINISHED'}


class ASSET_EXPORT_Select_Export(bpy.types.Operator):
	bl_idname = 'tae.select_export'
	bl_label = 'Select export'

	index: bpy.props.IntProperty()
	list: bpy.props.StringProperty()

	def execute(self, context):
		for obj in context.selected_objects:
			obj.select_set(False)

		if self.list == 'render':
			collection = context.scene.asset_export.rendered_objs[self.index].objs
		elif self.list == 'collision':
			collection = context.scene.asset_export.collision_objs[self.index].objs
		else:
			return {'CANCELLED'}

		for obj in collection:
			obj.obj.select_set(True)
			bpy.context.view_layer.objects.active = obj.obj
		return {'FINISHED'}


class ASSET_EXPORT_UL_list(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		if active_propname == 'selected_rendered':
			list = 'render'
			selected_idx = context.scene.asset_export.selected_rendered
		elif active_propname == 'selected_collision':
			list = 'collision'
			selected_idx = context.scene.asset_export.selected_collision

		selected = selected_idx == index

		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			# layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
			row = layout.row(align=True)
			row.prop(item, 'export', icon_only=True, icon='CHECKBOX_HLT' if item.export else 'CHECKBOX_DEHLT',
					 emboss=False, toggle=0)
			row.prop(item, 'name', text="", emboss=False, icon='MESH_DATA')
			# row.label(text=item.name, translate=False, icon='MESH_DATA')
			row.alignment = 'RIGHT'

			# if selected:
			# row.label(text='', icon='FILE_REFRESH')

			op = row.operator(ASSET_EXPORT_Select_Export.bl_idname, text=str(item.objs.__len__()), emboss=False)
			op.index = index
			op.list = list

		elif self.layout_type in {'GRID'}:
			layout.alignment = 'CENTER'
			layout.label(text="", icon='MESH_DATA')


class ASSET_EXPORT_Choose_Folder(bpy.types.Operator):
	"""Select save location"""
	bl_idname = 'tae.choose_folder'
	bl_label = 'Choose folder'

	use_filter_folder = True
	directory: bpy.props.StringProperty(name="Outdit Path", description="Export location")

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def execute(self, context):
		bpy.context.scene.asset_export.export_path = self.directory
		return {'FINISHED'}


# from bpy_extras.io_utils import ExportHelper
class ASSET_EXPORT_Export_Modal(bpy.types.Operator):
	"""Open export window dialog"""
	bl_idname = "tae.select_path"
	bl_label = "Select save location"

	use_filter_folder = True
	directory: bpy.props.StringProperty(name="Outdit Path", description="Export location")

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

	def draw(self, context):
		layout = self.layout
		row = layout.row()

		col = layout.column()
		row = col.row()
		row.label(text="Rendered Meshes", icon='SHADING_RENDERED')
		row.alignment = 'RIGHT'
		row.label(text=str(sum(o.export == True for o in context.scene.asset_export.rendered_objs)) + '/' + str(
			context.scene.asset_export.rendered_objs.keys().__len__()))

		col.template_list(
			"ASSET_EXPORT_UL_list", "rendered",
			bpy.context.scene.asset_export, 'rendered_objs',
			bpy.context.scene.asset_export, 'selected_rendered')

		layout.separator(factor=2)

		col = layout.column()
		row = col.row()
		row.label(text="Collision Meshes", icon='SHADING_WIRE')
		row.alignment = 'RIGHT'
		row.label(text=str(sum(o.export == True for o in context.scene.asset_export.collision_objs)) + '/' + str(
			context.scene.asset_export.collision_objs.keys().__len__()))

		col.template_list(
			"ASSET_EXPORT_UL_list", "collision",
			bpy.context.scene.asset_export, 'collision_objs',
			bpy.context.scene.asset_export, 'selected_collision')

	def execute(self, context):
		bpy.context.scene.asset_export.export_path = self.directory
		bpy.ops.tae.export_all('INVOKE_DEFAULT')
		return {'FINISHED'}


class ASSET_EXPORT_Export_All(bpy.types.Operator):
	"""Quick export to previous chosen path"""
	bl_idname = "tae.export_all"
	bl_label = "Export all enabled"

	bl_options = {'REGISTER'}

	def execute(self, context):
		filepath = bpy.context.scene.asset_export.export_path

		r_objs = bpy.context.scene.asset_export.rendered_objs
		for idx in range(r_objs.keys().__len__()):
			exp = r_objs[idx]
			if exp.export:
				bpy.ops.tae.select_export(index=idx, list='render')
				bpy.ops.export_scene.fbx(
					filepath=filepath + 'RDR-' + exp.name + '.fbx',
					check_existing=True,

					use_selection=True,
					axis_forward='-Z',
					axis_up='Y',

					object_types={'MESH'},
					use_mesh_modifiers=True,
					bake_anim=False)

		c_objs = bpy.context.scene.asset_export.collision_objs
		for idx in range(c_objs.keys().__len__()):
			exp = c_objs[idx]
			if exp.export:
				bpy.ops.tae.select_export(index=idx, list='collision')
				offset = bpy.context.object.location.copy()
				bpy.ops.transform.translate(value=-offset)

				bpy.ops.export_scene.obj(
					filepath=filepath + 'COL-' + exp.name + '.obj',
					check_existing=True,

					use_selection=True,
					axis_forward='-Z',
					axis_up='Y',

					use_mesh_modifiers=True,
					use_blen_objects=True,
					use_triangles=True,

					use_animation=False,
					use_uvs=False,
					use_materials=False,
					use_nurbs=False,
					use_vertex_groups=False,
					use_normals=False)

				bpy.ops.transform.translate(value=offset)

		return {'FINISHED'}


class ASSET_EXPORT_Panel(bpy.types.Panel):
	"""Creates a Panel in the context menu in View3D"""
	bl_idname = "TOOLS_PT_asset_export"
	bl_label = "Batch exporter panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_context = "objectmode"
	bl_category = "Asset Exporter"

	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout
		obj = context.object

		##########################

		col = layout.column()
		row = col.row()
		row.label(text="Rendered Meshes", icon='SHADING_RENDERED')
		row.alignment = 'RIGHT'
		row.label(text=str(sum(o.export == True for o in context.scene.asset_export.rendered_objs)) + '/' + str(
			context.scene.asset_export.rendered_objs.keys().__len__()))

		col.template_list("ASSET_EXPORT_UL_list", "rendered", bpy.context.scene.asset_export, 'rendered_objs',
						  bpy.context.scene.asset_export, 'selected_rendered')

		row = col.row(align=True)
		row.prop(context.scene.asset_export, 'current_render_name', text="")

		op = row.operator(ASSET_EXPORT_Add_Export.bl_idname, icon='ADD', text="")
		op.list = 'render'
		op.export_name = context.scene.asset_export.current_render_name

		op = row.operator(ASSET_EXPORT_Remove_Export.bl_idname, icon='REMOVE', text="")
		op.list = 'render'
		op.del_index = context.scene.asset_export.selected_rendered

		##########################	

		layout.separator(factor=2)

		##########################	

		col = layout.column()
		row = col.row()
		row.label(text="Collision Meshes", icon='SHADING_WIRE')
		row.alignment = 'RIGHT'
		row.label(text=str(sum(o.export == True for o in context.scene.asset_export.collision_objs)) + '/' + str(
			context.scene.asset_export.collision_objs.keys().__len__()))

		col.template_list("ASSET_EXPORT_UL_list", "collision", bpy.context.scene.asset_export, 'collision_objs',
						  bpy.context.scene.asset_export, 'selected_collision')

		row = col.row(align=True)
		row.prop(context.scene.asset_export, 'current_collision_name', text="")

		op = row.operator(ASSET_EXPORT_Add_Export.bl_idname, icon='ADD', text="")
		op.list = 'collision'
		op.export_name = context.scene.asset_export.current_collision_name

		op = row.operator(ASSET_EXPORT_Remove_Export.bl_idname, icon='REMOVE', text="")
		op.list = 'collision'
		op.del_index = context.scene.asset_export.selected_rendered

		###########################	

		layout.separator(factor=2)

		###########################

		# col = layout.column()
		# row = col.row()
		# row.label(text='Export')

		# row = col.row()
		# row.menu("INFO_MT_add", text='test')

		# col = layout.column(align=True)
		# row = col.row(align=True)
		# row.prop(context.scene.asset_export, 'export_path', text='')
		# op = row.operator(ASSET_EXPORT_Choose_Folder.bl_idname, icon='FILE_FOLDER', text='')
		# row = col.row(align=True)
		# row.enabled = context.scene.asset_export.export_path != ''
		# op = row.operator(ASSET_EXPORT_Export_All.bl_idname, icon='EXPORT', text='Export All')

		col = layout.column()
		row = col.row(align=True)
		op = row.operator(ASSET_EXPORT_Export_Modal.bl_idname, icon='FILEBROWSER', text='Export As')
		op = row.operator(ASSET_EXPORT_Export_All.bl_idname, icon='EXPORT', text='')


def register():
	bpy.utils.register_class(ASSET_EXPORT_obj_list)
	bpy.utils.register_class(ASSET_EXPORT_entry)
	bpy.utils.register_class(ASSET_EXPORT_data)
	bpy.types.Scene.asset_export = bpy.props.PointerProperty(type=ASSET_EXPORT_data)

	bpy.utils.register_class(ASSET_EXPORT_Add_Export)
	bpy.utils.register_class(ASSET_EXPORT_Remove_Export)
	bpy.utils.register_class(ASSET_EXPORT_Select_Export)
	bpy.utils.register_class(ASSET_EXPORT_Choose_Folder)

	bpy.utils.register_class(ASSET_EXPORT_UL_list)
	bpy.utils.register_class(ASSET_EXPORT_Export_Modal)
	bpy.utils.register_class(ASSET_EXPORT_Export_All)
	bpy.utils.register_class(ASSET_EXPORT_Panel)


def unregister():
	bpy.utils.unregister_class(ASSET_EXPORT_obj_list)
	bpy.utils.unregister_class(ASSET_EXPORT_entry)
	bpy.utils.unregister_class(ASSET_EXPORT_data)

	bpy.utils.unregister_class(ASSET_EXPORT_Add_Export)
	bpy.utils.unregister_class(ASSET_EXPORT_Remove_Export)
	bpy.utils.unregister_class(ASSET_EXPORT_Select_Export)
	bpy.utils.unregister_class(ASSET_EXPORT_Choose_Folder)

	bpy.utils.unregister_class(ASSET_EXPORT_UL_list)
	bpy.utils.unregister_class(ASSET_EXPORT_Export_Modal)
	bpy.utils.unregister_class(ASSET_EXPORT_Export_All)
	bpy.utils.unregister_class(ASSET_EXPORT_Panel)
