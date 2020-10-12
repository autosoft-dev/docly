import os
import shutil
from pathlib import Path
from typing import Dict
# from tabnanny import check

CACHE_DIR = (Path().home() / ".docly" / "file_cache")

cache_exists = lambda : CACHE_DIR.exists()
make_cache_dir = lambda : os.mkdir(str(CACHE_DIR))



def apply_diff(docstr_loc: Dict[str, Dict[int, tuple]]):
    try:
        for file_loc, docstrs in docstr_loc.items():
            # l = check(file_loc)
            temp_file_name = f"{str(Path(file_loc).stem)}.pytemp"
            final_file_name = f"{str(Path(file_loc).stem)}.py"
            temp_file = (Path(file_loc).parent / temp_file_name)
            final_file = (Path(file_loc).parent / final_file_name)
            write_handle = open(temp_file, "w")
            
            with open(file_loc) as f:
                for line_num, line in enumerate(f):
                    if docstrs.get(line_num+1):
                        docstr_line = docstrs.get(line_num+1)[1]
                        num_spaces = int(docstrs.get(line_num+1)[0])
                        spaces = " ".join([''] * (num_spaces + 1))
                        line_to_write = f'{spaces}"""\n{spaces}{docstr_line}\n{spaces}"""\n'
                        write_handle.write(line_to_write)
                        write_handle.write(line)
                    else:
                        write_handle.write(line)
            cache_file_name = file_loc[1:].replace("/", "#")
            
            if not cache_exists():
                make_cache_dir()
            
            if (CACHE_DIR / cache_file_name).exists():
                (CACHE_DIR / cache_file_name).unlink()
            
            shutil.move(file_loc, str(CACHE_DIR / cache_file_name))
            shutil.move(str(temp_file), str(final_file))

            write_handle.close()
    except KeyboardInterrupt:
        temp_file.unlink()
