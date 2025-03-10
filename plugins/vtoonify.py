#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class VToonify(GimpPluginBase):

    def run(self, style_num, style_id, style_degree, color_transfer, keep_size, force_cpu):
        self.model_file = "VToonify.py"
        self.name = _style_list[style_num][0]
        gfu.gimp.progress_init("Running VToonify ({}) ...".format(self.name))
        layer = self.drawable
        result = self.predict(layer, _style_list[style_num][1], style_id, style_degree, color_transfer, keep_size, force_cpu=force_cpu)
        if not result:
            return
        #h, w, _ = result.shape
        #self.gimp_img.resize(w, h, 0, 0)
        newlayer = self.create_layer(
            result, name=self.drawable.name + ":" + _style_list[style_num][0]
        )
	newlayer.set_offsets(layer.offsets[0], layer.offsets[1])


_style_list = [
    ("Arcane",                    "arcane"),
    ("Caricature1 (s039,d0.5)",   "caricature1"),
    ("Caricature2 (s068,d0.5)",   "caricature2"),
    ("Cartoon",                   "cartoon"),
    ("Comic",                     "comic"),
    ("Illustration1 (s004)",      "illustration1"),
    ("Illustration2 (s009)",      "illustration2"),
    ("Illustration3 (s043)",      "illustration3"),
    ("Illustration4 (s054)",      "illustration4"),
    ("Illustration5 (s086)",      "illustration5"),
    ("Pixar",                     "pixar"),
]

_style_params = (name for i, (name, style) in enumerate(_style_list))

plugin = VToonify()
plugin.register(
    proc_name="vtoonify",
    blurb="VToonify\nControllable High-Resolution Portrait Video Style Transfer",
    help="https://github.com/williamyang1991/DualStyleGAN/tree/main/doc_images",
    author="yantoz",
    copyright="",
    date="2023",
    label="Style Transfer (VToonify) ...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "style",          "Style:",         0,       _style_params),
        (gfu.PF_INT,    "style_id",       "Style ID",       26),
        (gfu.PF_FLOAT,  "style_degree",   "Style Degree",   0.5),
        (gfu.PF_BOOL,   "color_transfer", "Color Transfer", False),
        (gfu.PF_BOOL,   "keep_size",      "Keep Size",      True),
        (gfu.PF_BOOL,   "force_cpu",      "Force CPU",      False),
    ],
)
