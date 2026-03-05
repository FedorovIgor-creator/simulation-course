import numpy as np
import matplotlib.pyplot as plt

L = 0.10
T_mod = 2.0

rho = 500.0
lambda_ = 0.15
c = 1700.0

a = lambda_ / (rho * c)

T_initial = 100.0
T_boundary = 20.0


dt_values = [0.1, 0.01,0.001,0.0001]
dx_values = [0.1, 0.01,0.001,0.0001]

table = np.zeros((len(dt_values), len(dx_values)))

dt_plot = 0.01
dx_plot = 0.01


for i_dt, dt in enumerate(dt_values):
    for i_dx, dx in enumerate(dx_values):

        r = a * dt / dx**2

        if r > 0.5:
            table[i_dt, i_dx] = np.nan
            continue

        nx = int(L / dx) + 1
        x = np.linspace(0, L, nx)

        T = np.full(nx, T_initial)

        t = 0.0
        while t < T_mod:
            T_new = T.copy()

            for j in range(1, nx - 1):
                T_new[j] = T[j] + r * (T[j+1] - 2*T[j] + T[j-1])

            T_new[0] = T_boundary
            T_new[-1] = T_boundary

            T = T_new
            t += dt

        table[i_dt, i_dx] = T[nx // 2]

        if dt == dt_plot and dx == dx_plot:
            T_plot = T.copy()
            x_plot = x.copy()



print("\nТемпература в центре пластины через 2 секунды\n")

print("dt \\ dx", end="\t")
for dx in dx_values:
    print(dx, end="\t")
print()

for i, dt in enumerate(dt_values):
    print(dt, end="\t")
    for j in range(len(dx_values)):
        if np.isnan(table[i, j]):
            print("—", end="\t")
        else:
            print(f"{table[i, j]:.2f}", end="\t")
    print()


plt.figure(figsize=(8, 5))
plt.plot(x_plot, T_plot, linewidth=2)
plt.xlabel("Координата x, м")
plt.ylabel("Температура, °C")
plt.title("Распределение температуры в пластине через 2 с")
plt.grid(True)
plt.show()

