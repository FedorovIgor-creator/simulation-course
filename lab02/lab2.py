import numpy as np
import matplotlib.pyplot as plt

plate_length = 1.0                 # длина пластины (м)
thermal_diffusivity = 1e-4         # коэффициент температуропроводности (м²/с)
simulation_time = 2.0              # время моделирования (с)


time_steps_list = [0.1, 0.01, 0.001, 0.0001] 
space_steps_list = [0.1, 0.01, 0.001, 0.0001]    

#Таблица результатов: температура в центре для каждой пары (dt, dx)
results_table = np.zeros((len(time_steps_list), len(space_steps_list)))


plot_time_step = 0.01
plot_space_step = 0.01

#Перебор всех комбинаций шагов
for idx_dt, current_dt in enumerate(time_steps_list):
    for idx_dx, current_dx in enumerate(space_steps_list):

        # Число Фурье (критерий устойчивости явной схемы)
        fourier_number = thermal_diffusivity * current_dt / current_dx**2

        # Проверка устойчивости: если условие нарушено — пропускаем
        if fourier_number > 0.5:
            results_table[idx_dt, idx_dx] = np.nan
            continue

        num_nodes = int(plate_length / current_dx) + 1      # количество узлов сетки
        spatial_grid = np.linspace(0, plate_length, num_nodes)  # координаты узлов

        #Начальные условия
        temperature = np.zeros(num_nodes)                   
        temperature[num_nodes // 2] = 100.0                

        
        current_time = 0.0
        while current_time < simulation_time:
            temperature_new = temperature.copy()

            # Конечно-разностная аппроксимация (МКР) для внутренних узлов
            for node_idx in range(1, num_nodes - 1):
                temperature_new[node_idx] = (
                    temperature[node_idx] 
                    + fourier_number * (
                        temperature[node_idx + 1] 
                        - 2 * temperature[node_idx] 
                        + temperature[node_idx - 1]
                    )
                )

            # Граничные условия
            temperature_new[0] = 0
            temperature_new[-1] = 0

            temperature = temperature_new
            current_time += current_dt

        results_table[idx_dt, idx_dx] = temperature[num_nodes // 2]

        # Сохранение данных для графика при заданных параметрах
        if current_dt == plot_time_step and current_dx == plot_space_step:
            temperature_plot = temperature.copy()
            spatial_grid_plot = spatial_grid.copy()

print("\nТемпература в центре пластины через 2 секунды\n")

print("dt \\ dx", end="\t")
for dx_val in space_steps_list:
    print(dx_val, end="\t")
print()

for i, dt_val in enumerate(time_steps_list):
    print(dt_val, end="\t")
    for j in range(len(space_steps_list)):
        if np.isnan(results_table[i, j]):
            print("—", end="\t")
        else:
            print(f"{results_table[i, j]:.2f}", end="\t")
    print()

plt.figure(figsize=(8, 5))
plt.plot(spatial_grid_plot, temperature_plot, linewidth=2)
plt.xlabel("Координата x, м")
plt.ylabel("Температура, °C")
plt.title("Распределение температуры в пластине через 2 с")
plt.grid(True)
plt.show()