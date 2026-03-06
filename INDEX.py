"""
Perfil de Usuario — Python / Tkinter
Equivalente visual del diseño HTML con:
  - Fondo degradado en tonos verdes oscuros
  - Campos de visualización en gris claro
  - Modo edición / guardado / cancelar
  - Toast de confirmación
"""

# ─── Verificar dependencias ANTES de todo ────────────────────────────────────
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    _root = tk.Tk()
    _root.withdraw()
    messagebox.showerror(
        "Dependencia faltante",
        "Esta app requiere Pillow.\n\nInstala con:\n  pip install Pillow"
    )
    _root.destroy()
    raise SystemExit

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
import io
import threading


# ─── Paleta de colores ───────────────────────────────────────────────────────
BG_TOP      = "#0a1f14"
BG_MID      = "#124a2a"
BG_BOT      = "#081a10"
CARD_BG     = "#0f2d1a"
CARD_BORDER = "#1e5c30"
ACCENT      = "#39ff8e"
ACCENT_DIM  = "#1a9c5b"
TEXT_LIGHT  = "#e8f5ec"
TEXT_MUTED  = "#7aad8a"
FIELD_BG    = "#e8f5ec"   # gris-verdoso claro (vista)
FIELD_FG    = "#1a2e22"
FIELD_EDIT  = "#d6eedd"   # verde claro (edición)
LABEL_COLOR = "#4a9c6a"


# ─── Ventana principal ───────────────────────────────────────────────────────
root = tk.Tk()
root.title("Perfil de Usuario")
root.geometry("500x700")
root.resizable(False, False)
root.configure(bg=BG_TOP)


# ─── Fondo degradado ─────────────────────────────────────────────────────────
def crear_fondo_degradado(w, h):
    img = Image.new("RGB", (w, h))
    top = (10, 31, 20)
    bot = (8, 26, 16)
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        # CORREGIDO: era "bot[2] - bot[2]" (siempre 0), ahora "bot[2] - top[2]"
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(w):
            factor = 1 + 0.15 * (x / w)
            r2 = min(255, int(r * factor))
            g2 = min(255, int(g * 1.0 + 20 * (x / w)))
            b2 = min(255, b)
            img.putpixel((x, y), (r2, g2, b2))
    return img


canvas_bg = tk.Canvas(root, width=500, height=700, highlightthickness=0, bd=0)
canvas_bg.place(x=0, y=0, relwidth=1, relheight=1)

fondo_img_pil = crear_fondo_degradado(500, 700)
fondo_photo   = ImageTk.PhotoImage(fondo_img_pil)
canvas_bg.create_image(0, 0, anchor="nw", image=fondo_photo)


# ─── Card (frame redondeado con Canvas) ──────────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    pts = [
        x1+radius, y1,   x2-radius, y1,
        x2, y1,          x2, y1+radius,
        x2, y2-radius,   x2, y2,
        x2-radius, y2,   x1+radius, y2,
        x1, y2,          x1, y2-radius,
        x1, y1+radius,   x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


card_canvas = tk.Canvas(root, width=420, height=610,
                        bg=CARD_BG, highlightthickness=1,
                        highlightbackground=CARD_BORDER)
card_canvas.place(x=40, y=45)


# ─── Estado de la app ─────────────────────────────────────────────────────────
state = {
    "nombre": "Juan Pérez",
    "correo": "juan@email.com",
    "foto":   None,
    "editando": False,
    "snap": {}
}

avatar_photo_ref = None   # para evitar GC


# ─── Carga de avatar por defecto (desde URL) ──────────────────────────────────
def cargar_avatar_default():
    url = "https://api.dicebear.com/8.x/glass/svg?seed=Juan"
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            data = r.read()
        try:
            import cairosvg
            png = cairosvg.svg2png(bytestring=data, output_width=88, output_height=88)
            img = Image.open(io.BytesIO(png)).convert("RGBA")
        except Exception:
            img = Image.new("RGBA", (88, 88), "#1a5c30")
    except Exception:
        img = Image.new("RGBA", (88, 88), "#1a5c30")
    state["foto"] = img
    root.after(0, actualizar_avatar)


threading.Thread(target=cargar_avatar_default, daemon=True).start()


# ─── Avatar circular ──────────────────────────────────────────────────────────
AV_SIZE = 88
AV_X, AV_Y = 210, 28   # centro en card_canvas

def circle_image(img, size=AV_SIZE):
    img = img.resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, mask=mask)
    return out


# anillo degradado
ring_canvas = tk.Canvas(card_canvas, width=AV_SIZE+10, height=AV_SIZE+10,
                        bg=CARD_BG, highlightthickness=0)
ring_canvas.place(x=AV_X - (AV_SIZE+10)//2, y=AV_Y)

def draw_ring():
    s = AV_SIZE + 10
    ring_canvas.create_oval(0, 0, s, s, outline=ACCENT, width=3)

draw_ring()

# CORREGIDO: se añade imagen placeholder inicial para evitar colapso del label
_placeholder = Image.new("RGBA", (AV_SIZE, AV_SIZE), "#1a5c30")
_placeholder_ci = circle_image(_placeholder)
_placeholder_ref = ImageTk.PhotoImage(_placeholder_ci)

avatar_label = tk.Label(ring_canvas, bg=CARD_BG, image=_placeholder_ref)
avatar_label.image = _placeholder_ref   # referencia extra por seguridad
avatar_label.place(x=5, y=5, width=AV_SIZE, height=AV_SIZE)

def actualizar_avatar():
    global avatar_photo_ref
    if state["foto"] is None:
        return
    ci = circle_image(state["foto"])
    avatar_photo_ref = ImageTk.PhotoImage(ci)
    avatar_label.configure(image=avatar_photo_ref)

avatar_label.bind("<Button-1>", lambda e: cambiar_foto() if state["editando"] else None)


# ─── Nombre ─────────────────────────────────────────────────────────────
lbl_nombre = tk.Label(card_canvas, text=state["nombre"],
                      font=("Helvetica", 17, "bold"),
                      bg=CARD_BG, fg=TEXT_LIGHT)
lbl_nombre.place(x=210, y=132, anchor="n")


# ─── Separador ────────────────────────────────────────────────────────────────
sep = tk.Frame(card_canvas, height=1, bg=CARD_BORDER)
sep.place(x=20, y=182, width=380)


# ─── Helper: crear campo ──────────────────────────────────────────────────────
def crear_campo(parent, label_text, default_val, y_pos, es_select=False, opciones=None):
    lbl = tk.Label(parent, text=label_text,
                   font=("Helvetica", 8, "bold"),
                   bg=CARD_BG, fg=LABEL_COLOR)
    lbl.place(x=20, y=y_pos)

    display = tk.Label(parent, text=default_val,
                       font=("Helvetica", 12),
                       bg=FIELD_BG, fg=FIELD_FG,
                       anchor="w", padx=12,
                       relief="flat", bd=0)
    display.place(x=20, y=y_pos+18, width=380, height=36)

    if es_select:
        var = tk.StringVar(value=default_val)
        edit_widget = ttk.Combobox(parent, textvariable=var,
                                   values=opciones or [],
                                   state="readonly",
                                   font=("Helvetica", 12))
        edit_widget.place_forget()
    else:
        var = tk.StringVar(value=default_val)
        edit_widget = tk.Entry(parent, textvariable=var,
                               font=("Helvetica", 12),
                               bg=FIELD_EDIT, fg=FIELD_FG,
                               insertbackground=FIELD_FG,
                               relief="flat", bd=0, highlightthickness=1,
                               highlightbackground=ACCENT_DIM,
                               highlightcolor=ACCENT)
        edit_widget.place_forget()

    return {"label": lbl, "display": display,
            "edit": edit_widget, "var": var,
            "y": y_pos + 18, "es_select": es_select}


campos = {
    "nombre": crear_campo(card_canvas, "NOMBRE COMPLETO", state["nombre"], 200),
    "correo": crear_campo(card_canvas, "CORREO ELECTRÓNICO", state["correo"], 265),
}

# Estilo Combobox
style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox",
                fieldbackground=FIELD_EDIT,
                background=FIELD_EDIT,
                foreground=FIELD_FG,
                selectbackground=ACCENT_DIM,
                selectforeground=FIELD_FG)


# ─── Botones ──────────────────────────────────────────────────────────────────
BTN_Y = 420

def make_btn(parent, text, color_bg, color_fg, x, w, cmd):
    btn = tk.Button(parent, text=text,
                    bg=color_bg, fg=color_fg,
                    font=("Helvetica", 11, "bold"),
                    activebackground=ACCENT_DIM,
                    activeforeground="#021a0b",
                    relief="flat", bd=0, cursor="hand2",
                    command=cmd)
    btn.place(x=x, y=BTN_Y, width=w, height=40)
    return btn


btn_editar  = make_btn(card_canvas, "Editar perfil",   ACCENT,    "#021a0b", 20,  380, lambda: entrar_edicion())
btn_guardar = make_btn(card_canvas, "Guardar cambios", ACCENT,    "#021a0b", 20,  240, lambda: guardar())
btn_cancel  = make_btn(card_canvas, "Cancelar",        "#1e3d28", TEXT_LIGHT, 270, 130, lambda: cancelar())

btn_guardar.place_forget()
btn_cancel.place_forget()


# ─── Toast ────────────────────────────────────────────────────────────────────
toast_frame = tk.Frame(root, bg=ACCENT, padx=20, pady=8)
toast_lbl   = tk.Label(toast_frame, text="✓ Cambios guardados",
                       font=("Helvetica", 11, "bold"),
                       bg=ACCENT, fg="#021a0b")
toast_lbl.pack()

def show_toast():
    toast_frame.place(x=125, y=660)
    root.after(2500, hide_toast)

def hide_toast():
    toast_frame.place_forget()


# ─── Cambiar foto ─────────────────────────────────────────────────────────────
def cambiar_foto():
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
    )
    if ruta:
        img = Image.open(ruta).convert("RGBA")
        state["foto"] = img
        actualizar_avatar()


# ─── Lógica edición ───────────────────────────────────────────────────────────
def entrar_edicion():
    state["editando"] = True
    state["snap"] = {
        "nombre": campos["nombre"]["var"].get(),
        "correo": campos["correo"]["var"].get(),
        "foto":   state["foto"].copy() if state["foto"] else None,
    }
    for c in campos.values():
        c["display"].place_forget()
        c["edit"].place(x=20, y=c["y"], width=380, height=36)

    btn_editar.place_forget()
    btn_guardar.place(x=20,  y=BTN_Y, width=240, height=40)
    btn_cancel.place( x=270, y=BTN_Y, width=130, height=40)

    lbl_hint.configure(text="← clic en avatar para cambiar foto")


def cancelar():
    state["editando"] = False
    snap = state["snap"]
    campos["nombre"]["var"].set(snap["nombre"])
    campos["correo"]["var"].set(snap["correo"])
    if snap["foto"]:
        state["foto"] = snap["foto"]
        actualizar_avatar()

    for c in campos.values():
        c["edit"].place_forget()
        c["display"].place(x=20, y=c["y"], width=380, height=36)

    btn_guardar.place_forget()
    btn_cancel.place_forget()
    btn_editar.place(x=20, y=BTN_Y, width=380, height=40)
    lbl_hint.configure(text="")


def guardar():
    state["editando"] = False
    nombre = campos["nombre"]["var"].get().strip() or "Sin nombre"
    correo = campos["correo"]["var"].get().strip() or "—"

    campos["nombre"]["display"].configure(text=nombre)
    campos["correo"]["display"].configure(text=correo)

    lbl_nombre.configure(text=nombre)

    state["nombre"] = nombre
    state["correo"] = correo

    for c in campos.values():
        c["edit"].place_forget()
        c["display"].place(x=20, y=c["y"], width=380, height=36)

    btn_guardar.place_forget()
    btn_cancel.place_forget()
    btn_editar.place(x=20, y=BTN_Y, width=380, height=40)
    lbl_hint.configure(text="")
    show_toast()


# ─── Hint cambio foto ─────────────────────────────────────────────────────────
lbl_hint = tk.Label(card_canvas, text="",
                    font=("Helvetica", 9, "italic"),
                    bg=CARD_BG, fg=TEXT_MUTED)
lbl_hint.place(x=20, y=388)


# ─── Etiqueta inferior ────────────────────────────────────────────────────────
tk.Label(root, text="✦ Perfil de usuario",
         font=("Helvetica", 8),
         bg=BG_TOP, fg=LABEL_COLOR).place(x=50, y=50)


# ─── Centrar ventana ──────────────────────────────────────────────────────────
root.update_idletasks()
w = root.winfo_width()
h = root.winfo_height()
x = (root.winfo_screenwidth()  - w) // 2
y = (root.winfo_screenheight() - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")


root.mainloop()

