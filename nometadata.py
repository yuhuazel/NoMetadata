import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ExifTags
from tkinterdnd2 import DND_FILES, TkinterDnD

TkClass = TkinterDnD.Tk

def make_icon_shield(size=64, bg=(34,34,34), fg=(255,255,255)):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        (size*0.5, size*0.06),
        (size*0.92, size*0.28),
        (size*0.75, size*0.86),
        (size*0.5, size*0.98),
        (size*0.25, size*0.86),
        (size*0.08, size*0.28),
    ], fill=bg)
    draw.ellipse((size*0.4, size*0.32, size*0.6, size*0.52), fill=fg)
    draw.rectangle((size*0.46, size*0.52, size*0.54, size*0.72), fill=fg)
    return img

def make_icon_folder(size=64, bg=(60,60,60), band=(230,230,230)):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((size*0.08, size*0.28, size*0.92, size*0.8), fill=bg)
    draw.polygon([(size*0.08, size*0.28),(size*0.38, size*0.12),(size*0.6,size*0.12),(size*0.68,size*0.28)], fill=band)
    return img

_ORIENT_TRANSPOSE = {
    2: Image.FLIP_LEFT_RIGHT,
    3: Image.ROTATE_180,
    4: Image.FLIP_TOP_BOTTOM,
    5: Image.TRANSPOSE,
    6: Image.ROTATE_270,
    7: Image.TRANSVERSE,
    8: Image.ROTATE_90,
}

def fix_orientation(img):
    try:
        exif = img._getexif()
    except Exception:
        exif = None
    if not exif:
        return img
    orientation_key = None
    for k, v in ExifTags.TAGS.items():
        if v == 'Orientation':
            orientation_key = k
            break
    if not orientation_key:
        return img
    orientation = exif.get(orientation_key)
    op = _ORIENT_TRANSPOSE.get(orientation)
    if op:
        return img.transpose(op)
    return img

def strip_metadata_and_save(src_path: Path, dst_path: Path):
    try:
        with Image.open(src_path) as im:
            im.load()
            im = fix_orientation(im)
            fmt = im.format or src_path.suffix.replace('.', '').upper()
            if fmt.upper() in ('JPEG', 'JPG'):
                if im.mode in ('RGBA', 'LA'):
                    bg = Image.new('RGB', im.size, (255,255,255))
                    bg.paste(im, mask=im.split()[3])
                    im2 = bg
                else:
                    im2 = im.convert('RGB')
                im2.save(dst_path, 'JPEG', quality=95)
            elif fmt.upper() == 'PNG':
                if im.mode == 'P':
                    im2 = im.convert('RGBA')
                else:
                    im2 = im
                im2.save(dst_path, 'PNG')
            else:
                try:
                    im2 = im
                    im2.save(dst_path)
                except Exception:
                    im2 = im.convert('RGBA') if im.mode in ('P','LA','RGBA') else im.convert('RGB')
                    im2.save(dst_path, 'PNG')
        return True, ''
    except Exception as e:
        return False, str(e)

def unique_dst_path(output_dir: Path, original_name: str) -> Path:
    candidate = output_dir / original_name
    if not candidate.exists():
        return candidate
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    i = 1
    while True:
        new_name = f"{stem}({i}){suffix}"
        candidate = output_dir / new_name
        if not candidate.exists():
            return candidate
        i += 1

class App(TkClass):
    def __init__(self):
        super().__init__()
        self.title('No Metadata — Photo Metadata Remover')
        self.geometry('780x420')
        self.resizable(True, True)

        self.c_bg = '#1e1e1e'
        self.c_panel = '#2a2a2a'
        self.c_fg = '#f3f4f6'
        self.c_btn = '#3a3a3a'
        self.c_accent = '#4f8cff'
        self.configure(bg=self.c_bg)

        shield = make_icon_shield(size=64, bg=(40,40,40), fg=(240,240,240))
        folder = make_icon_folder(size=64, bg=(80,80,80), band=(240,240,240))
        self.ico_shield = ImageTk.PhotoImage(shield)
        self.ico_folder = ImageTk.PhotoImage(folder)

        top = tk.Frame(self, bg=self.c_bg)
        top.pack(side='top', fill='x', padx=12, pady=10)
        lbl = tk.Label(top, text='Select images, drag & drop files or folders, then click Remove Metadata', bg=self.c_bg, fg=self.c_fg, font=('Segoe UI', 11))
        lbl.pack(side='left', padx=6)
        icon_lbl = tk.Label(top, image=self.ico_shield, bg=self.c_bg)
        icon_lbl.pack(side='right')

        center = tk.Frame(self, bg=self.c_bg)
        center.pack(fill='both', expand=True, padx=12, pady=(0,12))
        left = tk.Frame(center, bg=self.c_bg)
        left.pack(side='left', fill='both', expand=True)

        self.dnd_hint = tk.Label(left, text='Drag & drop files or folders here', bg=self.c_panel, fg=self.c_fg, anchor='center')
        self.dnd_hint.pack(fill='x', padx=4, pady=(6,4))

        self.listbox = tk.Listbox(left, bg=self.c_panel, fg=self.c_fg, selectbackground=self.c_accent, selectforeground='#000000', highlightthickness=0, bd=0, activestyle='none')
        self.listbox.pack(side='left', fill='both', expand=True, padx=(0,6), pady=6)
        self.scroll = tk.Scrollbar(left, command=self.listbox.yview)
        self.scroll.pack(side='right', fill='y', pady=6)
        self.listbox.config(yscrollcommand=self.scroll.set)

        right = tk.Frame(center, width=220, bg=self.c_bg)
        right.pack(side='right', fill='y')
        tk.Button(right, text='Add Files', command=self.add_files, bg=self.c_btn, fg=self.c_fg, relief='flat').pack(fill='x', pady=(6,4), padx=6)
        tk.Button(right, text='Add Folder', command=self.add_folder, bg=self.c_btn, fg=self.c_fg, relief='flat').pack(fill='x', pady=4, padx=6)
        tk.Button(right, text='Remove Metadata', command=self.confirm_and_process, bg=self.c_accent, fg='#000000', relief='flat').pack(fill='x', pady=(20,6), padx=6)
        tk.Button(right, text='Clear List', command=self.clear_list, bg=self.c_btn, fg=self.c_fg, relief='flat').pack(fill='x', pady=4, padx=6)
        tk.Button(right, text='Exit', command=self.quit, bg=self.c_btn, fg=self.c_fg, relief='flat').pack(fill='x', pady=(40,6), padx=6)

        self.status_var = tk.StringVar(value='Ready')
        tk.Label(self, textvariable=self.status_var, anchor='w', bg=self.c_bg, fg=self.c_fg).pack(side='bottom', fill='x', padx=8, pady=6)

        self.img_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        self.base_dir = Path(sys.argv[0]).resolve().parent
        self.output_dir = self.base_dir / 'No Metadata'
        self.file_list = []

        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        import shlex
        try:
            parts = shlex.split(event.data)
        except Exception:
            parts = [p.strip('{}') for p in event.data.split()]
        self._add_paths(parts)

    def _add_paths(self, paths):
        added = 0
        for p in paths:
            p = p.strip('"').strip('{}')
            p = os.path.expanduser(p)
            p = os.path.normpath(p)
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    for name in files:
                        fp = Path(root) / name
                        if fp.suffix.lower() in self.img_exts and str(fp) not in self.file_list:
                            self.file_list.append(str(fp))
                            self.listbox.insert('end', str(fp))
                            added += 1
            else:
                fp = Path(p)
                if fp.suffix.lower() in self.img_exts and str(fp) not in self.file_list:
                    self.file_list.append(str(fp))
                    self.listbox.insert('end', str(fp))
                    added += 1
        self.status_var.set(f'Added {added} items' if added else 'No valid images found')

    def add_files(self):
        paths = filedialog.askopenfilenames(title='Select images', filetypes=[('Image files','*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp')])
        self._add_paths(paths)

    def add_folder(self):
        folder = filedialog.askdirectory(title='Select folder')
        if folder:
            self._add_paths([folder])

    def clear_list(self):
        if not self.file_list:
            self.status_var.set('List is empty')
            return
        last_index = len(self.file_list) - 1
        removed = self.file_list.pop(last_index)
        self.listbox.delete(last_index)
        self.status_var.set(f'Removed: {Path(removed).name}')

    def confirm_and_process(self):
        if not self.file_list:
            messagebox.showinfo('No files', 'Please add images first.')
            return
        if not messagebox.askokcancel('Confirm', f'Process {len(self.file_list)} files and save to "{self.output_dir}"?'):
            return
        threading.Thread(target=self._process_files_thread, daemon=True).start()

    def _process_files_thread(self):
        self.status_var.set('Processing...')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        succeeded, failed, total = 0, [], len(self.file_list)
        for i, f in enumerate(self.file_list, 1):
            try:
                src = Path(f)
                dst = unique_dst_path(self.output_dir, src.name)
                ok, err = strip_metadata_and_save(src, dst)
                if ok: succeeded += 1
                else: failed.append((str(src), err))
                self.status_var.set(f'Processing {i}/{total} — {succeeded} done')
            except Exception as e:
                failed.append((f, str(e)))
        msg = f'Finished. {succeeded} images saved to "{self.output_dir}".' if not failed else f'Finished with {succeeded} succeeded and {len(failed)} failed. See console for details.'
        for item, err in failed: print(item, err)
        self.status_var.set('Done')
        self.file_list.clear()
        self.listbox.delete(0, 'end')
        messagebox.showinfo('Done', msg)

def main():
    app = App()
    try: app.iconphoto(False, app.ico_shield)
    except Exception: pass
    app.mainloop()

if __name__ == '__main__':
    main()