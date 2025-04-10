from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)


from bpy.props import (
    BoolProperty,
    StringProperty,
    IntProperty,
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
            description = "Adds lightmaps to materials",
            default = True )

    use_blendmaps : BoolProperty(
            name = "Enable blendmaps",
            description = "Adds blendmaps to materials",
            default = True )

    remove_doubles : BoolProperty(
            name = "Merge vertices",
            description = "Removes double vertices",
            default = True )

    def execute(self, context):
        from . import import_mpk

        keywords = self.as_keywords(ignore=("filter_glob",))

        return import_mpk.load(self, context, **keywords)

    def draw(self, context):
        box = self.layout.box()
        box.prop( self, 'use_lightmaps' )
        box.prop( self, 'use_blendmaps' )
        box.prop( self, 'remove_doubles' )


def _optimization_switch(self, context):
    val = (self.use_preview << 2 | self.use_default << 1 | self.use_optimization << 0)
    match (self.opt_swt ^ val):
        case 0b100: # preview
            if (val & 0b100):
                if val & 0b010: self.use_default = False
                if val & 0b001: self.use_optimization = False
                self.opt_swt = 0b100
            else: self.use_preview = True
        case 0b010: # default
            if (val & 0b010):
                if val & 0b100: self.use_preview = False
                if val & 0b001: self.use_optimization = False
                self.opt_swt = 0b010
            else: self.use_default = True
        case 0b001: # optimize
            if (val & 0b001):
                if val & 0b100: self.use_preview = False
                if val & 0b010: self.use_default = False
                self.opt_swt = 0b001
            else: self.use_optimization = True


def _selection_switch(self, context):
    val = (self.use_all << 2 | self.use_selection << 1 | self.use_visible << 0)
    match (self.sel_swt ^ val):
        case 0b100: # all
            if (val & 0b100):
                if val & 0b010: self.use_selection = False
                if val & 0b001: self.use_visible = False
                self.sel_swt = 0b100
            else: self.use_all = True
        case 0b010: # selection
            if (val & 0b010):
                if val & 0b100: self.use_all = False
                if val & 0b001: self.use_visible = False
                self.sel_swt = 0b010
            else: self.use_selection = True
        case 0b001: # visible
            if (val & 0b001):
                if val & 0b100: self.use_all = False
                if val & 0b010: self.use_selection = False
                self.sel_swt = 0b001
            else: self.use_visible = True


@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportMPK(bpy.types.Operator, ExportHelper):
    """Export to MPK file format (.mpk)"""
    bl_idname = "export_scene.pkmpk"
    bl_label = 'Export MPK'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mpk"
    filter_glob: StringProperty(default="*.mpk", options={'HIDDEN'})
            
    opt_swt : IntProperty( default = 0b100 )

    use_preview : BoolProperty(
            name = "Preview",
            description = "Fast export for preliminary evaluation",
            default = True,
            update = _optimization_switch )

    use_default : BoolProperty(
            name = "Default",
            description = "Standard conversion",
            default = False,
            update = _optimization_switch )

    use_optimization : BoolProperty(
            name = "Optimize",
            description = "Remove double vertices.\n\n!!! TAKES LONG !!! 10 - 30 min\n\n" \
                            "Instead, export the data with the \'Preview' (or \'Default\') option,\n" \
                            "then import the data back into a new scene with the \'Merge vertices\'\n" \
                            "option (import dialog), and then export it with the \'Default\' option.\n"
                            "This way almost the same result as \'Optimize\'d is produced much faster",
            default = False,
            update = _optimization_switch )
            
    sel_swt : IntProperty( default = 0b100 )

    use_all: BoolProperty(
            name="All",
            description="Export all objects",
            default = True,
            update = _selection_switch )

    use_selection: BoolProperty(
            name="Selection",
            description="Export selected objects only",
            default = False,
            update = _selection_switch )

    use_visible: BoolProperty(
            name="Visible",
            description="Export visible objects only",
            default = False,
            update = _selection_switch )

    def execute(self, context):
        from . import export_mpk

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            "opt_swt",
                                            "sel_swt",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return export_mpk.load(self, context, **keywords)

    def draw(self, context):
        box = self.layout.box()
        box.prop( self, 'use_preview' )
        box.prop( self, 'use_default' )
        box.prop( self, 'use_optimization' )
        box.prop( self, 'use_all' )
        box.prop( self, 'use_selection' )
        box.prop( self, 'use_visible' )


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
