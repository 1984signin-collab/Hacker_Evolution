import ui.app
a = ui.app.HackerApp()
def check():
    cw = int(a._right_canvas.cget("width"))
    print("Right panel width:", cw)
    from data import HARDWARE
    for h in HARDWARE:
        name = h[0][:14]
        print(f'  HW name: "{name}" ({len(name)} chars)')
    items = a._right_canvas.find_withtag("hw")
    print(f"  HW items on canvas: {len(items)}")
    for item in items:
        bbox = a._right_canvas.bbox(item)
        if bbox:
            print(f"    bbox={bbox}")
a.root.after(12000, check)
a.root.after(15000, a.root.destroy)
a.root.mainloop()
