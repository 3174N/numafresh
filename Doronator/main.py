import tkinter as tk
import math


class HexButton:
    def __init__(self, canvas, center_x, center_y, size, hex_id):
        self.canvas = canvas
        self.hex_id_num = hex_id  # הקוד המספרי של המשושה
        
        # חישוב קודקודים לפי רדיוס (size) ומרכז (x, y)
        points = []
        for i in range(6):
            import math
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            px = center_x + size * math.cos(angle_rad)
            py = center_y + size * math.sin(angle_rad)
            points.extend([px, py])
            
        # יצירת הצורה על הקנבס
        self.shape = canvas.create_polygon(points, fill="#3498db", outline="white", width=2, activefill="#2980b9")
        
        # הוספת מספר במרכז
        canvas.create_text(center_x, center_y, text=str(hex_id), fill="white")
        
        # חיבור אירוע לחיצה
        canvas.tag_bind(self.shape, "<Button-1>", self.on_click)

    def on_click(self, event):
        print(f"נלחץ משושה מספר: {self.hex_id_num}")
        self.process_logic(self.hex_id_num)

    def process_logic(self, code):
        # כאן אתה מריץ את הפונקציation שלך לפי הקוד שהתקבל
        if code == 1:
            print("מריץ פונקציה עבור 1")
        elif code == 5:
            print("מפעיל מערכת...")

def create_grid(canvas, rows_list, size):
    count = 1
    # ריצה על המערך: r הוא אינדקס השורה, num_in_row הוא מספר המשושים באותה שורה
    for r, num_in_row in enumerate(rows_list):
        for c in range(num_in_row):
            # חישוב מיקום ה-X וה-Y
            # הוספנו indent כדי שהמשושים ישתלבו זה בזה (כוורת)
            x = 50 + c * (size * 1.75) + ((r % 2) * (size * 0.87))
            y = 50 + r * (size * 1.5)
            
            HexButton(canvas, x, y, size, count)
            count += 1
        

# הגדרת החלון
root = tk.Tk()
root.title("Hex Grid System")

canvas = tk.Canvas(root, width=600, height=500, bg="#2c3e50")
canvas.pack()

# יצירת גריד של 5 שורות על 5 עמודות
rows_config = [5, 4, 5, 4, 5]

create_grid(canvas, rows_config, size=30)

root.mainloop()