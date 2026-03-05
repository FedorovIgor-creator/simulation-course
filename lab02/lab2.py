import numpy as np
import matplotlib.pyplot as plt


L = 0.1            
T_mod = 2.0        

rho = 500.0         # Плотность
lambda_ = 0.15      # Теплопроводность
c = 1700.0          # Теплоемкость
 
Ts = 20.0           # температура на левой границе
Tn = 50.0           # температура на правой границе
T0 = 100.0          # начальная температура всей пластины

# Параметры сетки для исследования
dt_values = [0.1, 0.01]
dx_values = [0.1, 0.01]

table = np.zeros((len(dt_values), len(dx_values)))

dt_plot = 0.01
dx_plot = 0.01

print("Расчет по схеме (Метод прогонки)...")
print("-" * 60)

for i_dt, dt in enumerate(dt_values):
    for i_dx, dx in enumerate(dx_values):

        nx = int(L / dx) + 1      # Количество узлов
        h = dx                    # Шаг по пространству 
        tau = dt                  # Шаг по времени 
        
        x = np.linspace(0, L, nx) # Координатная сетка

        
        lambda_h2 = lambda_ / (h**2)       # λ / h²
        rho_c_tau = (rho * c) / tau        # ρc / τ

        # Коэффициенты A, B, C (они одинаковы для всех внутренних узлов)
        A = lambda_h2                      # A_i = C_i = λ/h²
        C = lambda_h2                      
        B = 2 * lambda_h2 + rho_c_tau      # B_i = 2λ/h² + ρc/τ

        T = np.full(nx, T0)              

        t = 0.0
        while t < T_mod:
            
            alpha = np.zeros(nx)
            beta = np.zeros(nx)
            
            # 1. ПРЯМАЯ ПРОГОНКА (движемся слева направо)

            alpha[0] = 0.0
            beta[0] = Ts
            
            for i in range(1, nx - 1):
                F = -rho_c_tau * T[i]
                
                denom = B - C * alpha[i-1]
                alpha[i] = A / denom
                beta[i] = (F + C * beta[i-1]) / denom
            
            # ОБРАТНАЯ ПРОГОНКА (движемся справа налево)
            T_new = np.zeros(nx)
            T_new[-1] = Tn
           
            for i in range(nx - 2, 0, -1):
                T_new[i] = alpha[i] * T_new[i+1] + beta[i]
            
            T_new[0] = Ts
          
            T = T_new
            t += tau

        table[i_dt, i_dx] = T[nx // 2] 

        if dt == dt_plot and dx == dx_plot:
            T_plot = T.copy()
            x_plot = x.copy()

print("\nТемпература в центре пластины через 2 секунды\n")
print("dt \\ dx", end="\t")
for dx_val in dx_values:
    print(f"{dx_val:.4f}", end="\t")
print()

for i, dt_val in enumerate(dt_values):
    print(f"{dt_val:.4f}", end="\t")
    for j in range(len(dx_values)):
        val = table[i, j]
        if np.isnan(val):
            print("—", end="\t")
        else:
            print(f"{val:.2f}", end="\t")
    print()


plt.figure(figsize=(8, 5))
plt.plot(x_plot, T_plot, 'b-', linewidth=2, label=f'dt={dt_plot}, dx={dx_plot}')
plt.xlabel("Координата x, м")
plt.ylabel("Температура, °C")
plt.title("Распределение температуры")
plt.grid(True)
plt.legend()
plt.show()
