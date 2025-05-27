import tkinter as tk
from tkinter import messagebox, filedialog
import csv, json, datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Datos principales
datos = {
    "salones": [],
    "jurados": {},
    "votantes": {},
    "asistencia": [],
    "resultados": [],
    "cedulas_registradas": set()
}

def generar_centro():
    try:
        sal = int(entry_sal.get())
        mes = int(entry_mes.get())
        jur = int(entry_jur.get())
        if sal <= 0 or mes <= 0 or jur <= 0:
            raise ValueError
        datos["salones"] = [[[None for _ in range(jur)] for _ in range(mes)] for _ in range(sal)]
        mostrar_botones()
    except:
        messagebox.showerror("Error", "Ingrese números válidos y positivos.")

def mostrar_botones():
    for widget in frame_botones.winfo_children():
        widget.destroy()
    for s, salon in enumerate(datos["salones"]):
        tk.Label(frame_botones, text=f"Salón {s+1}", font=("Arial", 10, "bold")).pack(anchor="w")
        for m, mesa in enumerate(salon):
            contenedor = tk.Frame(frame_botones); contenedor.pack(anchor="w", pady=2)
            tk.Button(contenedor, text=f"Mesa {m+1}", width=10, command=lambda s=s, m=m: mostrar_info_mesa(s, m)).pack(side="left")
            for j in range(len(mesa)):
                tk.Button(contenedor, text=f"Jurado {j+1}", width=10, command=lambda s=s, m=m, j=j: registrar_jurado(s, m, j)).pack(side="left", padx=1)

def registrar_jurado(s, m, j):
    top = tk.Toplevel(root); top.title("Registrar Jurado")
    tk.Label(top, text="Nombre:").pack(); entry_nombre = tk.Entry(top); entry_nombre.pack()
    tk.Label(top, text="Cédula:").pack(); entry_cedula = tk.Entry(top); entry_cedula.pack()
    tk.Label(top, text="Teléfono:").pack(); entry_telefono = tk.Entry(top); entry_telefono.pack()
    tk.Label(top, text="Dirección:").pack(); entry_direccion = tk.Entry(top); entry_direccion.pack()

    def guardar():
        nombre = entry_nombre.get().strip()
        cedula = entry_cedula.get().strip()
        telefono = entry_telefono.get().strip()
        direccion = entry_direccion.get().strip()
        if not all([nombre, cedula, telefono, direccion]):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios."); return
        if cedula in datos["cedulas_registradas"]:
            messagebox.showerror("Duplicado", "La cédula ya fue registrada."); return
        datos["jurados"][(s, m, j)] = {"nombre": nombre, "cedula": cedula, "telefono": telefono, "direccion": direccion}
        datos["cedulas_registradas"].add(cedula)
        messagebox.showinfo("Guardado", f"Jurado registrado en Salón {s+1}, Mesa {m+1}."); top.destroy()

    tk.Button(top, text="Guardar", command=guardar).pack(pady=5)

def mostrar_info_mesa(s, m):
    texto = f"Jurados registrados en Salón {s+1}, Mesa {m+1}:\n"
    for j in range(len(datos["salones"][s][m])):
        jurado = datos["jurados"].get((s, m, j))
        if jurado:
            texto += f"Jurado {j+1}: {jurado['nombre']} - {jurado['cedula']}\n"
    votantes = datos["votantes"].get((s, m), [])
    texto += f"\nVotantes asignados: {len(votantes)}\n"
    for v in votantes:
        texto += f"  {v['nombre']} - {v['cedula']}\n"
    messagebox.showinfo("Información de Mesa", texto)

def cargar_votantes():
    ruta = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    try:
        with open(ruta) as f:
            lector = csv.reader(f)
            next(lector)
            for nom, ced, sal, mes in lector:
                clave = (int(sal)-1, int(mes)-1)
                if clave not in datos["votantes"]:
                    datos["votantes"][clave] = []
                if ced in datos["cedulas_registradas"]:
                    raise Exception("Cédula duplicada")
                datos["votantes"][clave].append({"nombre": nom, "cedula": ced})
                datos["cedulas_registradas"].add(ced)
        messagebox.showinfo("Éxito", "Votantes cargados correctamente.")
    except:
        messagebox.showerror("Error", "Error al cargar el archivo CSV.")

def buscar_votante():
    cedula = entry_buscar_votante.get().strip()
    for (s, m), lista in datos["votantes"].items():
        for v in lista:
            if v["cedula"] == cedula:
                messagebox.showinfo("Resultado de Búsqueda", f"Votante encontrado:\nNombre: {v['nombre']}\nCédula: {v['cedula']}\nDebe votar en: Salón {s+1}, Mesa {m+1}")
                return
    messagebox.showinfo("No encontrado", "No se encontró ese votante.")

def registrar_asistencia():
    top = tk.Toplevel(root); top.title("Registrar Asistencia de Votante")
    tk.Label(top, text="Cédula del Votante:").pack()
    entry_cedula = tk.Entry(top); entry_cedula.pack()
    tk.Label(top, text="Salón (ej. Salón 1):").pack()
    entry_salon = tk.Entry(top); entry_salon.pack()
    tk.Label(top, text="Mesa (ej. Mesa 1):").pack()
    entry_mesa = tk.Entry(top); entry_mesa.pack()
    tk.Label(top, text="Hora (HH:MM, 24h):").pack()
    entry_hora = tk.Entry(top); entry_hora.pack()

    def guardar():
        cedula = entry_cedula.get().strip()
        salon = entry_salon.get().strip()
        mesa = entry_mesa.get().strip()
        hora = entry_hora.get().strip()
        try:
            hora_dt = datetime.datetime.strptime(hora, "%H:%M").time()
            if hora_dt > datetime.time(16, 0):
                raise ValueError("Hora inválida")
            datos["asistencia"].append({"cedula": cedula, "salon": salon, "mesa": mesa, "hora": hora})
            messagebox.showinfo("Registrado", "Asistencia registrada correctamente."); top.destroy()
        except:
            messagebox.showerror("Error", "Hora inválida o datos incorrectos.")

    tk.Button(top, text="Registrar", command=guardar).pack(pady=5)

# Interfaz principal
root = tk.Tk()
root.title("Simulador de Centro de Votación")

# Entradas
frame_entradas = tk.Frame(root)
frame_entradas.grid(row=0, column=0, sticky="w", padx=10, pady=10)

labels = ["Número de Salones:", "Número de Mesas por Salón:", "Número de Jurados por Mesa:"]
entries = []
for i, label_text in enumerate(labels):
    tk.Label(frame_entradas, text=label_text).grid(row=i, column=0, sticky="e")
    entry = tk.Entry(frame_entradas)
    entry.grid(row=i, column=1)
    entries.append(entry)

entry_sal, entry_mes, entry_jur = entries

frame_boton = tk.Frame(root)
frame_boton.grid(row=1, column=0, pady=5)

botones = [
    ("Generar Centro de Votación", generar_centro),
    ("Guardar Centro de Votación", lambda: None),
    ("Cargar Centro de Votación", lambda: None),
    ("Cargar Votantes", cargar_votantes),
    ("Registrar Asistencia", registrar_asistencia)
]
for texto, comando in botones:
    tk.Button(frame_boton, text=texto, width=25, command=comando).pack(pady=2)

# Buscadores
frame_buscar = tk.Frame(root)
frame_buscar.grid(row=2, column=0, pady=5)

entry_buscar_jurado = tk.Entry(frame_buscar)
entry_buscar_votante = tk.Entry(frame_buscar)

tk.Label(frame_buscar, text="Buscar Jurado por Cédula:").grid(row=0, column=0, sticky="e")
entry_buscar_jurado.grid(row=0, column=1, sticky="w")
tk.Button(frame_buscar, text="Buscar", command=lambda: None).grid(row=0, column=2)

tk.Label(frame_buscar, text="Buscar Votante por Cédula:").grid(row=1, column=0, sticky="e")
entry_buscar_votante.grid(row=1, column=1, sticky="w")
tk.Button(frame_buscar, text="Buscar", command=buscar_votante).grid(row=1, column=2)

# Área dinámica
frame_botones = tk.Frame(root)
frame_botones.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)

root.mainloop()