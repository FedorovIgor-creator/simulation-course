import tkinter as tk
from tkinter import ttk
import random
import math

# Константы состояний клетки
STATE_TREE = 0      # Зелёное дерево
STATE_FIRE = 1      # Горит
STATE_ASH = 2       # Пепел (сгорело)
STATE_REGROW = 3    # Восстановление
STATE_WATER = 4     # Вода

# Цвета для отображения (однотонные)
COLORS = {
    STATE_TREE:   "#228B22",   # Forest Green
    STATE_FIRE:   "#FF4500",   # Orange Red
    STATE_ASH:    "#3d3d3d",   # Dark Gray
    STATE_REGROW: "#90EE90",   # Light Green
    STATE_WATER:  "#1E90FF"    # Dodger Blue
}

class ForestFireSim:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Симулятор Лесных Пожаров 🔥")
        self.root.configure(bg="#1a1a2e")
        
        # Параметры сетки 100x100
        self.rows = 100
        self.cols = 100
        self.cell_size = 6#Пиксели
        
        # Параметры симуляции
        self.burn_duration = 5 #клетка горит 5 кадров
        self.ash_duration = 8 #клетка пепла 8 кадров
        self.regrow_duration = 10 #клетка растёт 10 кадров
        self.fire_spread_chance = 0.7#шанс распространения огня
        self.wind_direction = random.choice(['none', 'left', 'right', 'up', 'down'])
        self.wind_strength = 0.2
        
        # Состояния системы
        self.grid = []          # Текущее состояние каждой клетки
        self.timers = []        # Таймеры для каждой клетки
        self.is_running = True  # Запущена ли анимация
        self.lightning_mode = False
        self.water_mode = False
        self.fire_mode = False
        
        # Создание интерфейса
        self.create_widgets()
        self.init_grid()
        
        # Запуск анимации
        self.update_simulation()
        
    def create_widgets(self):
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)#расстягивается по ширине и высоте
        
        # Левая часть - канвас с сеткой
        canvas_frame = tk.Frame(main_frame, bg="#1a1a2e")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заголовок
        title = tk.Label(canvas_frame, text="🌲 ЛЕСНЫЕ ПОЖАРЫ 100×100 🌲", 
                        font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#FFD700")
        title.pack(pady=5)
        
        # Канвас для сетки
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.cols * self.cell_size, 
                               height=self.rows * self.cell_size,
                               bg="#0d0d1a", highlightthickness=2, highlightbackground="#444")
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Правая часть - панель управления
        control_frame = tk.Frame(main_frame, bg="#2a2a3e", width=250)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_frame.pack_propagate(False)
        
        # Заголовок панели
        tk.Label(control_frame, text="УПРАВЛЕНИЕ", 
                font=("Arial", 12, "bold"), bg="#2a2a3e", fg="#FFD700").pack(pady=10)
        
        # Кнопки управления
        buttons = [
            ("🔥 Пожар", self.toggle_fire_mode, "#FF6B6B"),
            ("💧 Вода", self.toggle_water_mode, "#4ECDC4"),
            ("⚡ Молния", self.activate_lightning, "#FFE66D"),
            ("☢️ Ядерный взрыв", self.nuclear_explosion, "#FF0000"),
            ("🌱 Восстановить", self.regrow_forest, "#95E1D3"),
            ("⏸️ Пауза/Старт", self.toggle_pause, "#F38181"),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(control_frame, text=text, command=command, 
                           bg=color, fg="white", font=("Arial", 10, "bold"),
                           width=20, height=2, relief=tk.RAISED)
            btn.pack(pady=5, padx=10)
        
        # Разделитель
        tk.Frame(control_frame, height=2, bg="#444").pack(fill=tk.X, pady=10, padx=10)
        
        # Статистика
        tk.Label(control_frame, text="СТАТИСТИКА", 
                font=("Arial", 11, "bold"), bg="#2a2a3e", fg="#FFD700").pack(pady=5)
        
        self.stat_labels = {}
        stats = [
            ("🌲 Деревья:", "tree_count", "#228B22"),
            ("🔥 Огонь:", "fire_count", "#FF4500"),
            ("💧 Вода:", "water_count", "#1E90FF"),
            ("⬛ Пепел:", "ash_count", "#3d3d3d"),
        ]
        
        for label_text, var_name, color in stats:
            frame = tk.Frame(control_frame, bg=color, padx=5, pady=3)
            frame.pack(fill=tk.X, padx=10, pady=2)
            label = tk.Label(frame, text=f"{label_text} 0", 
                            font=("Arial", 9, "bold"), bg=color, fg="white",
                            anchor=tk.W)
            label.pack(fill=tk.X)
            self.stat_labels[var_name] = label
        
        # Разделитель
        tk.Frame(control_frame, height=2, bg="#444").pack(fill=tk.X, pady=10, padx=10)
        
        # Настройки
        tk.Label(control_frame, text="НАСТРОЙКИ", 
                font=("Arial", 11, "bold"), bg="#2a2a3e", fg="#FFD700").pack(pady=5)
        
        settings_frame = tk.Frame(control_frame, bg="#2a2a3e")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(settings_frame, text="Шанс огня:", 
                bg="#2a2a3e", fg="white", font=("Arial", 9)).pack(side=tk.LEFT)
        self.chance_slider = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
                                       value=0.7, orient=tk.HORIZONTAL,
                                       command=self.update_chance)
        self.chance_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.chance_label = tk.Label(settings_frame, text="70%", 
                                    bg="#2a2a3e", fg="#FFD700", width=5,
                                    font=("Arial", 9))
        self.chance_label.pack(side=tk.RIGHT)
        
        # Режим
        self.mode_label = tk.Label(control_frame, text="Режим: Просмотр", 
                                  font=("Arial", 10, "bold"), 
                                  bg="#2a2a3e", fg="#00FF00", pady=10)
        self.mode_label.pack(fill=tk.X, padx=10)
        
        # Легенда
        tk.Label(control_frame, text="ЛЕГЕНДА", 
                font=("Arial", 10, "bold"), bg="#2a2a3e", fg="#FFD700").pack(pady=5)
        
        legend_frame = tk.Frame(control_frame, bg="#2a2a3e")
        legend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        legend_items = [
            ("Дерево", "#228B22"),
            ("Огонь", "#FF4500"),
            ("Пепел", "#3d3d3d"),
            ("Рост", "#90EE90"),
            ("Вода", "#1E90FF"),
        ]
        
        for text, color in legend_items:
            item_frame = tk.Frame(legend_frame, bg="#2a2a3e")
            item_frame.pack(fill=tk.X, pady=1)
            
            color_box = tk.Canvas(item_frame, width=20, height=15, bg=color, highlightthickness=0)
            color_box.pack(side=tk.LEFT)
            
            tk.Label(item_frame, text=text, bg="#2a2a3e", fg="white", 
                    font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        # Информация об озёрах
        tk.Label(control_frame, text="🏞️ ОЗЁРА", 
                font=("Arial", 10, "bold"), bg="#2a2a3e", fg="#1E90FF").pack(pady=5)
        self.lake_info = tk.Label(control_frame, text="Озеро 1: ~300 клеток\nОзеро 2: ~300 клеток", 
                                  font=("Arial", 8), bg="#2a2a3e", fg="#87CEEB", justify=tk.LEFT)
        self.lake_info.pack(padx=10, pady=5)
    
    def create_lake(self, center_row, center_col, target_cells=300):
        """Создаёт озеро эллиптической формы вокруг центра"""
        lake_cells = []
        
        # Подбираем размер эллипса для получения ~target_cells
        for a in range(5, 20):  # Полуось A
            for b in range(5, 20):  # Полуось B
                cells = []
                for dr in range(-a, a+1):
                    for dc in range(-b, b+1):
                        # Проверка попадания в эллипс
                        if (dr*dr)/(a*a) + (dc*dc)/(b*b) <= 1:
                            r, c = center_row + dr, center_col + dc
                            if 0 <= r < self.rows and 0 <= c < self.cols:
                                cells.append((r, c))
                
                if len(cells) >= target_cells - 20 and len(cells) <= target_cells + 20:
                    return cells#размер озера должен быть в диапазоне
        
        # Если не нашли точный размер, возвращаем лучший вариант
        a, b = 12, 12
        for dr in range(-a, a+1):
            for dc in range(-b, b+1):
                if (dr*dr)/(a*a) + (dc*dc)/(b*b) <= 1:
                    r, c = center_row + dr, center_col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        lake_cells.append((r, c))
        
        return lake_cells[:target_cells]
    
    def init_grid(self):
        """Инициализация сетки 100x100 с двумя озёрами"""
        self.grid = [[STATE_TREE for _ in range(self.cols)] for _ in range(self.rows)]
        self.timers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Создаём два озера в разных частях карты
        # Озеро 1: верхний левый квадрат
        lake1_center = (25, 25)
        lake1_cells = self.create_lake(lake1_center[0], lake1_center[1], 300)
        
        # Озеро 2: нижний правый квадрат
        lake2_center = (75, 75)
        lake2_cells = self.create_lake(lake2_center[0], lake2_center[1], 300)
        
        # Заполняем озёра водой
        for r, c in lake1_cells + lake2_cells:
            self.grid[r][c] = STATE_WATER
        
        self.lake1_count = len(lake1_cells)
        self.lake2_count = len(lake2_cells)
        
        self.draw_grid()
        self.update_stats()
    
    def draw_grid(self):#отрисовка
        """Отрисовка сетки (однотонные клетки)"""
        self.canvas.delete("all")
        
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                state = self.grid[row][col]
                color = COLORS[state]
                
                # Рисуем однотонный прямоугольник без эффектов
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    
    def on_canvas_click(self, event):
        """Обработка клика по канвасу"""
        col = event.x // self.cell_size #переводим пиксели в номер клетки
        row = event.y // self.cell_size
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.lightning_mode:
                self.lightning_strike(row, col) #режим молнии, поджигает клетку
                self.lightning_mode = False
                self.mode_label.config(text="Режим: Просмотр", fg="#00FF00")
            elif self.water_mode:#режим воды
                self.grid[row][col] = STATE_WATER#ставит воду
                self.timers[row][col] = 0
                self.draw_grid()
                self.update_stats()
            elif self.fire_mode:#пожар-можно поджечь только деревья
                if self.grid[row][col] == STATE_TREE:
                    self.grid[row][col] = STATE_FIRE
                    self.timers[row][col] = self.burn_duration
                    self.draw_grid()
                    self.update_stats()
    
    def toggle_fire_mode(self):
        self.fire_mode = True
        self.water_mode = False
        self.lightning_mode = False
        self.mode_label.config(text="Режим: Пожар (клик)", fg="#FF6B6B")
    
    def toggle_water_mode(self):
        self.water_mode = True
        self.fire_mode = False
        self.lightning_mode = False
        self.mode_label.config(text="Режим: Вода (клик)", fg="#4ECDC4")
    
    def activate_lightning(self):
        self.lightning_mode = True
        self.fire_mode = False
        self.water_mode = False
        self.mode_label.config(text="Режим: Молния (клик)", fg="#FFE66D")
    
    def lightning_strike(self, row, col):
        """Удар молнии - 20 клеток вокруг"""
        for dr in range(-5, 6):
            for dc in range(-5, 6):
                if dr*dr + dc*dc <= 25:
                    r, c = row + dr, col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        if self.grid[r][c] == STATE_TREE:
                            self.grid[r][c] = STATE_FIRE
                            self.timers[r][c] = self.burn_duration
        self.draw_grid()
        self.update_stats()
    
    def nuclear_explosion(self):
        """Ядерный взрыв - всё поле горит"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != STATE_WATER:
                    self.grid[row][col] = STATE_FIRE
                    self.timers[row][col] = self.burn_duration
        self.draw_grid()
        self.update_stats()
    
    def regrow_forest(self):
        """Восстановить весь лес (озёра сохраняются)"""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != STATE_WATER:
                    self.grid[row][col] = STATE_TREE
                    self.timers[row][col] = 0
        self.draw_grid()
        self.update_stats()
    
    def toggle_pause(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.mode_label.config(text="Режим: Просмотр", fg="#00FF00")
        else:
            self.mode_label.config(text="Режим: ПАУЗА", fg="#FF0000")
    
    def update_chance(self, value):#изменение шанса возгорания
        self.fire_spread_chance = float(value)
        self.chance_label.config(text=f"{int(float(value)*100)}%")
    
    def update_simulation(self):
        """Основной цикл симуляции"""
        if self.is_running:
            new_grid = [row[:] for row in self.grid]
            new_timers = [row[:] for row in self.timers]#создаём копии массивов
            
            for row in range(self.rows):
                for col in range(self.cols):
                    state = self.grid[row][col]
                    timer = self.timers[row][col]#проходим по каждой клетке
                    
                    if state == STATE_FIRE:#елси клетка горит
                        new_timers[row][col] = timer - 1
                        if new_timers[row][col] <= 0:
                            new_grid[row][col] = STATE_ASH
                            new_timers[row][col] = self.ash_duration
                        self.spread_fire(row, col, new_grid, new_timers)
                    
                    elif state == STATE_ASH:#если клетка пепел
                        new_timers[row][col] = timer - 1
                        if new_timers[row][col] <= 0:
                            new_grid[row][col] = STATE_REGROW
                            new_timers[row][col] = self.regrow_duration
                    
                    elif state == STATE_REGROW:#восстановление
                        new_timers[row][col] = timer - 1
                        if new_timers[row][col] <= 0:
                            new_grid[row][col] = STATE_TREE
                            new_timers[row][col] = 0
                    
                    elif state == STATE_TREE:#процент случайного возгорания
                        if random.random() < 0.001:
                            new_grid[row][col] = STATE_FIRE
                            new_timers[row][col] = self.burn_duration
            
            self.grid = new_grid
            self.timers = new_timers
            self.draw_grid()
            self.update_stats()
        
        self.root.after(150, self.update_simulation)#каждый кадр на 150млсек
    
    def spread_fire(self, row, col, new_grid, new_timers):
        """Распространение огня"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]#4 напрлвения
        
        wind_bonus = {
            'right': [0, 1, 0, 0],# Ветер вправо → бонус ко второму направлению  (0,1)
            'left': [1, 0, 0, 0],
            'down': [0, 0, 1, 0],
            'up': [0, 0, 0, 1],
            'none': [0, 0, 0, 0]
        }
        
        for i, (dr, dc) in enumerate(directions):
            nr, nc = row + dr, col + dc# Координаты соседа
            
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid[nr][nc] == STATE_TREE:
                    chance = self.fire_spread_chance
                    if wind_bonus[self.wind_direction][i] == 1:
                        chance += self.wind_strength
                    
                    if random.random() < chance:
                        new_grid[nr][nc] = STATE_FIRE
                        new_timers[nr][nc] = self.burn_duration
    
    def update_stats(self):
        """Обновление статистики"""
        tree_count = 0
        fire_count = 0
        water_count = 0
        ash_count = 0
        
        for row in range(self.rows):
            for col in range(self.cols):
                state = self.grid[row][col]
                if state == STATE_TREE:
                    tree_count += 1
                elif state == STATE_FIRE:
                    fire_count += 1
                elif state == STATE_WATER:
                    water_count += 1
                elif state in [STATE_ASH, STATE_REGROW]:
                    ash_count += 1
        
        self.stat_labels["tree_count"].config(text=f"🌲 Деревья: {tree_count}")
        self.stat_labels["fire_count"].config(text=f"🔥 Огонь: {fire_count}")
        self.stat_labels["water_count"].config(text=f"💧 Вода: {water_count}")
        self.stat_labels["ash_count"].config(text=f"⬛ Пепел: {ash_count}")
        
        # Обновляем информацию об озёрах
        self.lake_info.config(text=f"Озеро 1: ~{self.lake1_count} клеток\nОзеро 2: ~{self.lake2_count} клеток\nДобавлено: {water_count - self.lake1_count - self.lake2_count}")

def main():
    root = tk.Tk()
    root.geometry("850x700")
    root.resizable(True, True)
    app = ForestFireSim(root)
    root.mainloop()

if __name__ == "__main__":
    main()