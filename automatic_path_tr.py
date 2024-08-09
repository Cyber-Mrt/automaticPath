from __future__ import annotations
from typing import List, Tuple

import numpy as np
import rsplan
from matplotlib.animation import FuncAnimation, PillowWriter

import matplotlib as plt
plt.use('TkAgg')
import matplotlib.pyplot as plt

points = []
cid = None
runway_length = 5
turn_radius = 4.5
ani = None

"""
Eğer ani değişkenini global olarak tanımlamazsak, 
FuncAnimation nesnesi fonksiyonun bitişiyle birlikte yok olur ve animasyon çalışmaz. 
Bu yüzden, ani değişkenini global olarak tanımlayarak ve fonksiyon içinde ona değer atayarak animasyonun yaşam döngüsünü kontrol altına aldık.
"""

def _get_yaw() -> float:
    """Kullanıcıdan yaw değerini alır"""
    while True:
        try:
            yaw = float(input("Enter yaw (degrees): "))
            yaw = np.deg2rad(yaw)
            return yaw
        except ValueError:
            print("Invalid input. Please enter a number.")

def _plot_arrow(
        x: float,
        y: float,
        yaw: float,
        length: float = 0.5,
        width: float = 1.0,
        label: str = ""
) -> None:
    """Ok çizimini yapar"""
    plt.arrow(
        x,
        y,
        length * np.cos(yaw),
        length * np.sin(yaw),
        head_width=width,
        head_length=width,
    )
    plt.plot(x, y, marker="s", label=label)

def _visualize_path(ax, rs_path: rsplan.Path) -> None:
    """Verilen yolu görselleştirir"""
    
    x_coords, y_coords, yaw = rs_path.coordinates_tuple()
    ax.clear()
    plt.grid(True)
    ax_limitor(ax, rs_path)
    _plot_arrow(x_coords[0], y_coords[0], yaw[0], label="Start")
    _plot_arrow(x_coords[-1], y_coords[-1], yaw[-1], label="End")

    ax.plot(x_coords, y_coords, "r-")  # Kırmızı çizgi
    plt.gcf().canvas.mpl_connect("button_press_event", _onclick)
    plt.draw()
    
    # Animasyonu başlat
    global ani
    ani = animation(rs_path, ax)

def _onclick(event) -> None:
    global points, cid
    if event.xdata is not None and event.ydata is not None:
        if len(points) == 0:
            plt.plot(event.xdata, event.ydata, marker="s", label="Start")
        elif len(points) == 1:
            plt.plot(event.xdata, event.ydata, marker="s", label="End")
        points.append((event.xdata, event.ydata))
        plt.draw()

        if len(points) == 2:
            plt.gcf().canvas.mpl_disconnect(cid)

            # When two points are selected, path is calculated rest of the code is for path calculation
            start_yaw = _get_yaw()
            end_yaw = _get_yaw()
            start_comb = (points[0][0], points[0][1], start_yaw)
            end_comb = (points[1][0], points[1][1], end_yaw)
            global path
            # Path hesaplanır
            path = path_calculator(start_comb, end_comb)

            _visualize_path(ax, path)

def path_calculator(start_comb: Tuple[float, float, float], end_comb: Tuple[float, float, float]) -> rsplan.Path:
    """Verilen başlangıç ve bitiş noktaları ile yolu hesaplar"""

    # rsplan modülünden gelen path fonksiyonu ile yolu hesaplar

    path = rsplan.path(start_comb, end_comb, turn_radius, runway_length, 0.05)
    return path

def animation(path: rsplan.Path, ax) -> FuncAnimation:
    """Animasyonu çalıştırır"""
    x_coords, y_coords, yaw = path.coordinates_tuple()
    line, = ax.plot([], [], "k-", lw=3)

    def _init() -> Tuple:
        line.set_data([], [])
        return line,

    def _animate(i: int) -> Tuple:
        line.set_data(x_coords[:i], y_coords[:i])
        return line,

    ani = FuncAnimation(plt.gcf(), _animate, frames=len(x_coords), init_func=_init, interval=10, blit=False)
    
   
    return ani

def _run() -> None:
    """Kullanıcıdan alınan koordinatlar ile yolu hesaplar ve görselleştirir"""
    global points, ax
    fig, ax = plt.subplots()
    plt.grid(True)

    ax.set_ylim(-20, 20)
    ax.set_xlim(-20, 20)

    plt.gcf().canvas.mpl_connect("button_press_event", _onclick)  # When mouse is clicked, _onclick function is called
    plt.show()

def ax_limitor(ax: plt.Axes, rs_path: rsplan.Path) -> None:
    """Eksen limitlerini ayarlar"""
    x_coords, y_coords, yaw = rs_path.coordinates_tuple()
    ax.set_xlim(min(x_coords) - 2, max(x_coords) + 2)
    ax.set_ylim(min(y_coords) - 2, max(y_coords) + 2)

if __name__ == "__main__":
    _run()
