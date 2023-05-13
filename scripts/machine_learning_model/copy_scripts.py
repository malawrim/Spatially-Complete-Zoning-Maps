#!/usr/bin/env python3

"""
Use to duplicate the generic_zoning_script.py for all necessary model iterations.

Output: Creates new python files with filenames that correspond to those listed in test_names

Usage: copy_scripts.py
"""
import shutil

test_names = [
    "within_core",
    "within_sub",
    "between_core_r1",
    "between_core_r2",
    "between_core_r3",
    "between_core_r4",
    "between_core_r5",
    "between_core_r6",
    "between_core_r7",
    "between_core_r8",
    "between_core_r9",
    "between_core_r10",
    "between_core_r11",
    "between_core_r12",
    "between_core_r13",
    "between_core_r14",
    "between_core_r15",
    "between_sub_r1",
    "between_sub_r2",
    "between_sub_r3",
    "between_sub_r4",
    "between_sub_r5",
    "between_sub_r6",
    "between_sub_r7",
    "between_sub_r8",
    "between_sub_r9",
    "between_sub_r10",
    "between_sub_r11",
    "between_sub_r12",
    "between_sub_r13",
    "between_sub_r14",
    "between_sub_r15",
]

for t in test_names:
    out_file = t + ".py"
    shutil.copy("generic_zoning_script.py", out_file)
