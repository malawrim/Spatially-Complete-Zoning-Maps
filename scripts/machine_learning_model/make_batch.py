"""
If running zoning model on HPC, use this script to create bash scripts for all model runs. 
See generic_zoning_script.py and copy_scripts.py

Output: creates new batch files with filenames that correspond to those listed in test_names

Usage: make_batch.py
"""

import sys
import os

test_names = [
    "between_core_low",
    "between_sub_low",
    "between_core_high",
    "between_sub_high",
    "within_core",
    "within_sub",
    "within_sub_80_20",
    "within_sub_50_50",
    "within_sub_20_80",
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
    outfile = t + ".csh"
    f = open(outfile, "w")
    f.write(
        """#!/bin/tcsh\n#BSUB -n 16\n#BSUB -W 600\n#BSUB -R "span[hosts=1]"\n#BSUB -q shared_memory\n#BSUB -J """
    )
    f.write(t)
    f.write("\n#BSUB -o stdout_")
    f.write(t)
    f.write("\n#BSUB -e stderr_")
    f.write(t)
    f.write(
        """\nmodule load PrgEnv-intel\nconda activate /usr/local/usrapps/rkmeente/malawrim/zone_python\nmpirun python """
    )
    f.write(t)
    f.write(""".py\nconda deactivate""")
    f.close()
