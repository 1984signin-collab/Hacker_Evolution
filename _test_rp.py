import ui.app
a = ui.app.HackerApp()
def check():
    cw = a._right_canvas.winfo_width()
    ch = a._right_canvas.winfo_height()
    print("Right canvas:", cw, "x", ch)
    items = a._right_canvas.find_withtag("hw")
    for item in items:
        bbox = a._right_canvas.bbox(item)
        if bbox:
            print("  hw bbox:", bbox)
    obj_items = a._right_canvas.find_withtag("obj")
    for item in obj_items:
        bbox = a._right_canvas.bbox(item)
        if bbox:
            print("  obj bbox:", bbox)
    all_items = a._right_canvas.find_all()
    max_y = 0
    for item in all_items:
        bbox = a._right_canvas.bbox(item)
        if bbox:
            max_y = max(max_y, bbox[3])
    print("Content max Y:", max_y, "vs canvas H:", ch)
a.root.after(12000, check)
a.root.after(15000, a.root.destroy)
a.root.mainloop()
