import ui.app
a = ui.app.HackerApp()
def check():
    cw = int(a._right_canvas.cget("width"))
    print("Right canvas width:", cw)
    print("Right canvas actual:", a._right_canvas.winfo_width())
    from engine.game import g
    for s in g.servers:
        if "pos" in s:
            print(f'  {s["name"]}: pos={s["pos"]}')
        else:
            print(f'  {s["name"]}: NO POS')
    print("Map canvas:", a.map_canvas.winfo_width(), "x", a.map_canvas.winfo_height())
    print("Map anim frame:", a._map_renderer._anim_frame)
a.root.after(12000, check)
a.root.after(15000, a.root.destroy)
a.root.mainloop()
