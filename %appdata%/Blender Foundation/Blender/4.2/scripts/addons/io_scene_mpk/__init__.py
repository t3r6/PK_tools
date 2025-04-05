from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)


from bpy.props import (
    BoolProperty,
    StringProperty,
)


import bpy
bl_info = {
    "name": "Painkiller MPK format",
    "author": "dilettante",
    "version": (3, 0, 0),
    "blender": (4, 2, 2),
    "location": "File > Import-Export",
    "description": "Painkiller WorldMesh Import",
    "doc_url": "https://github.com/max-ego/PK_tools/",
    "category": "Import-Export",
}


if "bpy" in locals():
    import importlib
    if "import_mpk" in locals():
        importlib.reload(import_mpk)
    if "export_mpk" in locals():
        importlib.reload(export_mpk)


class ImportMPK(bpy.types.Operator, ImportHelper):
    """Import from MPK file format (.mpk)"""
    bl_idname = "import_scene.pkmpk"
    bl_label = 'Import MPK'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mpk"
    filter_glob: StringProperty(default="*.mpk", options={'HIDDEN'})

    use_lightmaps : BoolProperty(
            name = "Enable lightmaps",
            description = "Add lightmaps to materials",
            default = True )

    use_blendmaps : BoolProperty(
            name = "Enable blendmaps",
            description = "Add blendmaps to materials",
            default = True )

    remove_doubles : BoolProperty(
            name = "Merge vertices",
            description = "Remove double vertices",
            default = False )

    def execute(self, context):
        from . import import_mpk

        keywords = self.as_keywords(ignore=("filter_glob",))

        return import_mpk.load(self, context, **keywords)

    def draw(self, context):
        box = self.layout.box()
        box.prop( self, 'use_lightmaps' )
        box.prop( self, 'use_blendmaps' )
        box.prop( self, 'remove_doubles' )


@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportMPK(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.pkmpk"
    bl_label = 'Export MPK'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mpk"
    filter_glob: StringProperty(default="*.mpk", options={'HIDDEN'})

    use_optimization : BoolProperty(
            name = "Optimize",
            description = "Remove double vertices",
            default = False )

    
    use_selection: BoolProperty(
            name="Selection",
            description="Export selected objects only",
            default = False )

    def execute(self, context):
        from . import export_mpk

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return export_mpk.load(self, context, **keywords)

    def draw(self, context):
        box = self.layout.box()
        box.prop( self, 'use_optimization' )
        box.prop( self, 'use_selection' )


# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(ImportMPK.bl_idname, text="Painkiller WorldMesh (.mpk)")


def menu_func_export(self, context):
    self.layout.operator(ExportMPK.bl_idname, text="Painkiller WorldMesh (.mpk)")


def register():
    bpy.utils.register_class(ImportMPK)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ExportMPK)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportMPK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportMPK)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
