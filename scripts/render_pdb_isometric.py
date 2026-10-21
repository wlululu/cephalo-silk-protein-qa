#!/usr/bin/env python3
"""VMD NewCartoon isometric rendering of existing PDB files.

Based on the archived VMD notebook: white background, structure colors,
NewCartoon, perspective camera, yaw 45 degrees then pitch 30 degrees,
TachyonInternal TGA render converted to PNG. Requires VMD and Pillow.
Not validated as pixel-identical with historical images.
"""
import argparse, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdb-dir',required=True,type=Path)
    p.add_argument('--out-dir',required=True,type=Path)
    p.add_argument('--vmd',default='vmd')
    args=p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    vmd=shutil.which(args.vmd)
    if vmd is None:raise SystemExit('VMD binary not found; use --vmd /path/to/vmd')
    pdbs=sorted(args.pdb_dir.glob('*.pdb'))
    if not pdbs:raise SystemExit('No input PDB files found')
    for pdb in pdbs:
        png=args.out_dir/(pdb.stem+'_isometric.png')
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td);tcl=tmp/'render.tcl';tga=tmp/'render.tga'
            # Paths are quoted for Tcl; reject special characters that may alter the script.
            for path in (pdb,tga):
                if any(x in str(path) for x in ['"','{','}','\n','\r']):
                    raise ValueError('Unsupported path character: '+str(path))
            tcl.write_text(f"""mol new "{pdb.resolve().as_posix()}"
display projection Perspective
color Display Background white
mol delrep 0 top
mol representation NewCartoon
mol color Structure
mol addrep top
axes location off
display resetview
rotate y by 45
rotate x by 30
render TachyonInternal "{tga.as_posix()}"
quit
""")
            subprocess.run([vmd,'-dispdev','text','-e',str(tcl)],check=True)
            if not tga.exists():raise RuntimeError('No TGA rendered for '+pdb.name)
            with Image.open(tga) as img:
                # The historical source notebook used a 2x Lanczos resize.
                img.resize((img.width*2,img.height*2),Image.Resampling.LANCZOS).save(png)
        print(png)
if __name__=='__main__':main()
