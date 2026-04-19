import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.stats import chisquare
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings

# ---------- Константы ----------
VALUES = np.array([1, 2, 3, 4])
NS = [10, 100, 1000, 10000]

# ---------- Вспомогательные функции ----------
def generate_discrete(N, probs):
    return np.random.choice(VALUES, size=N, p=probs)

def generate_normal(N):
    return np.random.normal(0, 1, size=N)

def analyze(sample, N, probs, true_mean, true_var):
    counts = np.array([np.sum(sample == v) for v in VALUES])
    emp_p = counts / N
    
    mean = np.mean(sample)
    var = np.var(sample, ddof=0)  # смещённая оценка (соответствует теоретической дисперсии ген. совокупности)
    
    rel_m = abs(mean - true_mean) / true_mean
    rel_v = abs(var - true_var) / true_var

    # Подавляем предупреждение о малых ожидаемых частотах (допустимо для учебных целей при N=10)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        chi2, p = chisquare(counts, probs * N)

    return emp_p, mean, var, rel_m, rel_v, chi2, p


# ---------- GUI ----------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Имитационное моделирование СВ")
        root.geometry("1000x750")

        style = ttk.Style()
        style.theme_use("clam")

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.tabs)
        self.tab2 = ttk.Frame(self.tabs)
        self.tabs.add(self.tab1, text="Дискретная СВ")
        self.tabs.add(self.tab2, text="Нормальная СВ")

        # Состояние модели (вместо global)
        self.probs = np.array([0.25, 0.25, 0.25, 0.25])
        self.update_theoretical()

        self.build_discrete()
        self.build_normal()

    def update_theoretical(self):
        """Пересчёт теоретического среднего и дисперсии при изменении вероятностей"""
        self.true_mean = np.sum(VALUES * self.probs)
        self.true_var = np.sum((VALUES - self.true_mean) ** 2 * self.probs)

    # ---------- ДИСКРЕТНАЯ ВКЛАДКА ----------
    def build_discrete(self):
        control = ttk.Frame(self.tab1)
        control.pack(side="top", fill="x", pady=5)

        prob_frame = ttk.Frame(control)
        prob_frame.pack(side="left", padx=10)

        self.prob_entries = []
        for v in VALUES:
            ttk.Label(prob_frame, text=f"P({v})").grid(row=0, column=v-1)
            entry = ttk.Entry(prob_frame, width=6)
            entry.grid(row=1, column=v-1)
            entry.insert(0, str(self.probs[v-1]))
            self.prob_entries.append(entry)

        ttk.Button(control, text="РАВНОМЕРНОЕ", command=self.set_uniform_probs).pack(side="left", padx=10)
        ttk.Button(control, text="Запустить моделирование", command=self.run_discrete).pack(side="left", padx=10)

        # Таблица результатов
        self.tree = ttk.Treeview(self.tab1,
                                columns=("N", "Mean", "Var", "ErrMean", "ErrVar", "Chi2", "p"),
                                show="headings", height=6)
        headers = {
            "N": "N", "Mean": "Среднее", "Var": "Дисперсия",
            "ErrMean": "δ(ср.)", "ErrVar": "δ(дисп.)", "Chi2": "χ²", "p": "p-значение"
        }
        for c in self.tree["columns"]:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=110)
        self.tree.pack(fill="x", pady=10)

        # Графики
        self.fig1 = Figure(figsize=(8, 5))
        self.ax_d1 = self.fig1.add_subplot(221)
        self.ax_d2 = self.fig1.add_subplot(222)
        self.ax_d3 = self.fig1.add_subplot(223)
        self.ax_d4 = self.fig1.add_subplot(224)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Блок вывода
        self.conclusion_label = ttk.Label(self.tab1, text="Нажмите 'Запустить моделирование' для получения результатов.",
                                          wraplength=950, justify="left", foreground="blue")
        self.conclusion_label.pack(pady=5)

    def set_uniform_probs(self):
        for entry in self.prob_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "0.25")
        self.probs = np.array([0.25] * 4)
        self.update_theoretical()

    def run_discrete(self):
        try:
            new_probs = np.array([float(e.get()) for e in self.prob_entries])
            if np.any(new_probs < 0):
                raise ValueError("Вероятности не могут быть отрицательными")
            if abs(new_probs.sum() - 1.0) > 1e-6:
                raise ValueError("Сумма вероятностей должна быть равна 1")
            self.probs = new_probs
            self.update_theoretical()
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return
        except Exception:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
            return

        self.tree.delete(*self.tree.get_children())
        axes = [self.ax_d1, self.ax_d2, self.ax_d3, self.ax_d4]
        for ax in axes:
            ax.clear()

        last_rm, last_rv, last_p = 0.0, 0.0, 0.0

        for i, N in enumerate(NS):
            sample = generate_discrete(N, self.probs)
            emp_p, mean, var, rm, rv, chi2, p = analyze(sample, N, self.probs, self.true_mean, self.true_var)

            self.tree.insert("", "end",
                             values=(N, round(mean, 4), round(var, 4),
                                     round(rm, 4), round(rv, 4),
                                     round(chi2, 4), round(p, 4)))

            axes[i].hist(sample,
                         bins=np.arange(VALUES.min(), VALUES.max()+2)-0.5,
                         density=True, alpha=0.8, color='skyblue', edgecolor='black')
            axes[i].set_xticks(VALUES)
            axes[i].set_title(f"N = {N}")
            axes[i].grid(True, linestyle=':', alpha=0.6)

            last_rm, last_rv, last_p = rm, rv, p

        self.fig1.suptitle("Дискретное распределение: гистограммы эмпирических выборок")
        self.fig1.tight_layout(rect=[0, 0.05, 1, 0.93])
        self.canvas1.draw()

        # Автоматический вывод по заданию
        hyp = "не отвергается" if last_p >= 0.05 else "отвергается"
        conclusion = (
            f"🔍 Вывод:\n"
            f"• При увеличении N выборочные характеристики сходятся к теоретическим.\n"
            f"• При N={NS[-1]} отн. погрешность среднего: {last_rm:.3%}, дисперсии: {last_rv:.3%}.\n"
            f"• Критерий χ²: p={last_p:.4f} (гипотеза о соответствии закону {hyp} на уровне α=0.05)."
        )
        self.conclusion_label.config(text=conclusion)

    # ---------- НОРМАЛЬНАЯ ВКЛАДКА ----------
    def build_normal(self):
        control = ttk.Frame(self.tab2)
        control.pack(side="top", fill="x", pady=5)
        ttk.Button(control, text="Запустить моделирование", command=self.run_normal).pack(side="left", padx=10)

        self.fig2 = Figure(figsize=(8, 5))
        self.ax_n1 = self.fig2.add_subplot(221)
        self.ax_n2 = self.fig2.add_subplot(222)
        self.ax_n3 = self.fig2.add_subplot(223)
        self.ax_n4 = self.fig2.add_subplot(224)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)

        self.normal_conclusion = ttk.Label(self.tab2, text="Нажмите кнопку для построения графиков.",
                                           wraplength=950, justify="left")
        self.normal_conclusion.pack(pady=5)

    def run_normal(self):
        axes = [self.ax_n1, self.ax_n2, self.ax_n3, self.ax_n4]
        for ax in axes:
            ax.clear()

        x = np.linspace(-4, 4, 400)
        pdf = (1 / np.sqrt(2*np.pi)) * np.exp(-x**2 / 2)

        for i, N in enumerate(NS):
            sample = generate_normal(N)
            axes[i].hist(sample, bins=30, density=True, alpha=0.6, color='salmon', edgecolor='black')
            axes[i].plot(x, pdf, linewidth=2, color='navy', label='N(0,1)')
            axes[i].set_title(f"N = {N}")
            axes[i].grid(True, linestyle=':', alpha=0.6)
            if i == 0:
                axes[i].legend()

        self.fig2.suptitle("Нормальное распределение: сходимость гистограммы к плотности")
        self.fig2.tight_layout(rect=[0, 0.05, 1, 0.93])
        self.canvas2.draw()

        self.normal_conclusion.config(
            text="🔍 Вывод: С увеличением N форма гистограммы всё точнее аппроксимирует теоретическую кривую плотности нормального распределения N(0,1)."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()