# ---------------------------------------------------------------------
# Licensed to NADI System Corp. under a Contributor Agreement.
# See https://www.nadi3docms.com/ for licensing details.
#
# Inspector BIM For Blender
# Copyright (c) 2022-2023 by Eos Wolfuardian  All rights reserved.
#
# eos.chen@nadisystem.com
# https://www.linkedin.com/in/roy-yu-791202/
# Tool Concept:
#
# 步驟1 => 步驟2
# --------------------------------------------------------------------
# The Inspector BIM For Blender toolkit is
#
# Copyright (c) 2022-2023 by Eos Wolfuardian
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# NADI System Corp. or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# NADI System Corp. AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------
import os
import sys
import site

bl_info = {
    "name": "InspectorBIM",
    "description": "Analyze, create and modify data using BIM objects format",
    "author": "Eos Wolfuardian",
    "blender": (3, 3, 3),
    "version": (0, 0, 230504),
    "location": "View3D > UI > Inspector BIM",
    "category": "Inspector",
}

if sys.modules.get("bpy", None):
    site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))

    import inspectorbim.bim

    def register():
        inspectorbim.ifc.register()

    def unregister():
        inspectorbim.ifc.unregister()
