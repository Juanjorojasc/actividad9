import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv
import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CentroVotacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Centro de Votación")
        self.root.geometry("900x700")
        
        # Datos principales
        self.datos = {
            "configuracion": {"salones": 0, "mesas": 0, "jurados": 0},
            "salones": [],
            "jurados": {},
            "votantes": {},
            "asistencia": [],
            "resultados": [],
            "cedulas_registradas": set()
        }
        
        # Interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame de configuración
        frame_config = tk.LabelFrame(self.root, text="Configuración del Centro", padx=5, pady=5)
        frame_config.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame_config, text="Número de Salones:").grid(row=0, column=0, sticky="e")
        self.entry_sal = tk.Entry(frame_config)
        self.entry_sal.grid(row=0, column=1, sticky="w")
        
        tk.Label(frame_config, text="Número de Mesas por Salón:").grid(row=1, column=0, sticky="e")
        self.entry_mes = tk.Entry(frame_config)
        self.entry_mes.grid(row=1, column=1, sticky="w")
        
        tk.Label(frame_config, text="Número de Jurados por Mesa:").grid(row=2, column=0, sticky="e")
        self.entry_jur = tk.Entry(frame_config)
        self.entry_jur.grid(row=2, column=1, sticky="w")
        
        tk.Button(frame_config, text="Generar Centro", command=self.generar_centro).grid(row=3, columnspan=2, pady=5)
        
        # Frame de operaciones
        frame_ops = tk.LabelFrame(self.root, text="Operaciones", padx=5, pady=5)
        frame_ops.pack(pady=10, padx=10, fill="x")
        
        tk.Button(frame_ops, text="Guardar Configuración", command=self.guardar_configuracion).grid(row=0, column=0, padx=2)
        tk.Button(frame_ops, text="Cargar Configuración", command=self.cargar_configuracion).grid(row=0, column=1, padx=2)
        tk.Button(frame_ops, text="Cargar Votantes", command=self.cargar_votantes).grid(row=0, column=2, padx=2)
        tk.Button(frame_ops, text="Registrar Asistencia", command=self.registrar_asistencia).grid(row=0, column=3, padx=2)
        tk.Button(frame_ops, text="Cargar Resultados", command=self.cargar_resultados).grid(row=0, column=4, padx=2)
        tk.Button(frame_ops, text="Resumen Estadístico", command=self.mostrar_resumen).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(frame_ops, text="Generar Gráficos", command=self.generar_graficos).grid(row=1, column=2, columnspan=2, pady=5)
        
        # Frame de búsqueda
        frame_busqueda = tk.LabelFrame(self.root, text="Búsqueda", padx=5, pady=5)
        frame_busqueda.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame_busqueda, text="Buscar Jurado por Cédula:").grid(row=0, column=0, sticky="e")
        self.entry_buscar_jurado = tk.Entry(frame_busqueda)
        self.entry_buscar_jurado.grid(row=0, column=1, sticky="w")
        tk.Button(frame_busqueda, text="Buscar", command=self.buscar_jurado).grid(row=0, column=2, padx=5)
        
        tk.Label(frame_busqueda, text="Buscar Votante por Cédula:").grid(row=1, column=0, sticky="e")
        self.entry_buscar_votante = tk.Entry(frame_busqueda)
        self.entry_buscar_votante.grid(row=1, column=1, sticky="w")
        tk.Button(frame_busqueda, text="Buscar", command=self.buscar_votante).grid(row=1, column=2, padx=5)
        
        # Frame de visualización
        self.frame_botones = tk.LabelFrame(self.root, text="Estructura del Centro", padx=5, pady=5)
        self.frame_botones.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Scrollbar para el frame de botones
        self.canvas = tk.Canvas(self.frame_botones)
        self.scrollbar = ttk.Scrollbar(self.frame_botones, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def generar_centro(self):
        try:
            sal = int(self.entry_sal.get())
            mes = int(self.entry_mes.get())
            jur = int(self.entry_jur.get())
            
            if sal <= 0 or mes <= 0 or jur <= 0:
                raise ValueError("Los valores deben ser positivos")
            
            self.datos["configuracion"] = {"salones": sal, "mesas": mes, "jurados": jur}
            self.datos["salones"] = [[[None for _ in range(jur)] for _ in range(mes)] for _ in range(sal)]
            
            self.mostrar_botones()
            messagebox.showinfo("Éxito", "Centro de votación generado correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
    
    def mostrar_botones(self):
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        sal = self.datos["configuracion"]["salones"]
        mes = self.datos["configuracion"]["mesas"]
        jur = self.datos["configuracion"]["jurados"]
        
        for s in range(sal):
            salon_frame = tk.LabelFrame(self.scrollable_frame, text=f"Salón {s+1}", padx=5, pady=5)
            salon_frame.pack(fill="x", padx=5, pady=5)
            
            for m in range(mes):
                mesa_frame = tk.Frame(salon_frame)
                mesa_frame.pack(anchor="w", pady=2)
                
                tk.Button(
                    mesa_frame, 
                    text=f"Mesa {m+1}", 
                    width=10, 
                    command=lambda s=s, m=m: self.mostrar_info_mesa(s, m)
                ).pack(side="left")
                
                for j in range(jur):
                    tk.Button(
                        mesa_frame, 
                        text=f"Jurado {j+1}", 
                        width=10,
                        command=lambda s=s, m=m, j=j: self.registrar_jurado(s, m, j)
                    ).pack(side="left", padx=1)
    
    def registrar_jurado(self, salon_idx, mesa_idx, jurado_idx):
        top = tk.Toplevel(self.root)
        top.title(f"Registrar Jurado - Salón {salon_idx+1}, Mesa {mesa_idx+1}, Jurado {jurado_idx+1}")
        top.geometry("400x300")
        
        tk.Label(top, text="Nombre:").pack()
        entry_nombre = tk.Entry(top)
        entry_nombre.pack()
        
        tk.Label(top, text="Cédula:").pack()
        entry_cedula = tk.Entry(top)
        entry_cedula.pack()
        
        tk.Label(top, text="Teléfono:").pack()
        entry_telefono = tk.Entry(top)
        entry_telefono.pack()
        
        tk.Label(top, text="Dirección:").pack()
        entry_direccion = tk.Entry(top)
        entry_direccion.pack()
        
        def guardar():
            nombre = entry_nombre.get().strip()
            cedula = entry_cedula.get().strip()
            telefono = entry_telefono.get().strip()
            direccion = entry_direccion.get().strip()
            
            if not all([nombre, cedula, telefono, direccion]):
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            
            if not cedula.isdigit():
                messagebox.showwarning("Error", "La cédula debe contener solo números")
                return
            
            if cedula in self.datos["cedulas_registradas"]:
                messagebox.showerror("Error", "Esta cédula ya está registrada")
                return
            
            self.datos["jurados"][(salon_idx, mesa_idx, jurado_idx)] = {
                "nombre": nombre,
                "cedula": cedula,
                "telefono": telefono,
                "direccion": direccion
            }
            
            self.datos["cedulas_registradas"].add(cedula)
            messagebox.showinfo("Éxito", "Jurado registrado correctamente")
            top.destroy()
        
        tk.Button(top, text="Guardar", command=guardar).pack(pady=10)
    
    def mostrar_info_mesa(self, salon_idx, mesa_idx):
        info = f"Información de Salón {salon_idx+1}, Mesa {mesa_idx+1}\n\n"
        
        # Jurados
        info += "Jurados:\n"
        jurados_mesa = []
        for j in range(self.datos["configuracion"]["jurados"]):
            jurado = self.datos["jurados"].get((salon_idx, mesa_idx, j))
            if jurado:
                jurados_mesa.append(jurado)
                info += f"- {jurado['nombre']} (Cédula: {jurado['cedula']})\n"
        
        if not jurados_mesa:
            info += "No hay jurados registrados\n"
        
        # Votantes
        info += "\nVotantes asignados:\n"
        votantes = self.datos["votantes"].get((salon_idx, mesa_idx), [])
        for v in votantes:
            info += f"- {v['nombre']} (Cédula: {v['cedula']})\n"
        
        if not votantes:
            info += "No hay votantes asignados\n"
        
        # Asistencia
        info += "\nAsistencia registrada:\n"
        asistencias = [a for a in self.datos["asistencia"] 
                      if a.get("salon") == f"Salón {salon_idx+1}" 
                      and a.get("mesa") == f"Mesa {mesa_idx+1}"]
        
        for a in asistencias:
            info += f"- {a['cedula']} a las {a['hora']}\n"
        
        if not asistencias:
            info += "No hay asistencias registradas\n"
        
        messagebox.showinfo("Información de Mesa", info)
    
    def cargar_votantes(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de votantes",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        try:
            with open(ruta, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        salon = int(row['salon']) - 1
                        mesa = int(row['mesa']) - 1
                        cedula = row['cedula']
                        
                        if cedula in self.datos["cedulas_registradas"]:
                            raise ValueError(f"Cédula duplicada: {cedula}")
                        
                        if (salon, mesa) not in self.datos["votantes"]:
                            self.datos["votantes"][(salon, mesa)] = []
                        
                        self.datos["votantes"][(salon, mesa)].append({
                            "nombre": row['nombre'],
                            "cedula": cedula
                        })
                        
                        self.datos["cedulas_registradas"].add(cedula)
                    
                    except (KeyError, ValueError) as e:
                        messagebox.showwarning("Advertencia", f"Error en línea: {str(e)}")
                        continue
            
            messagebox.showinfo("Éxito", "Votantes cargados correctamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def buscar_jurado(self):
        cedula = self.entry_buscar_jurado.get().strip()
        
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula para buscar")
            return
        
        for key, jurado in self.datos["jurados"].items():
            if jurado["cedula"] == cedula:
                salon_idx, mesa_idx, jurado_idx = key
                info = (
                    f"Jurado encontrado:\n\n"
                    f"Nombre: {jurado['nombre']}\n"
                    f"Cédula: {jurado['cedula']}\n"
                    f"Teléfono: {jurado['telefono']}\n"
                    f"Dirección: {jurado['direccion']}\n\n"
                    f"Asignado a:\n"
                    f"Salón {salon_idx+1}, Mesa {mesa_idx+1}, Jurado {jurado_idx+1}"
                )
                messagebox.showinfo("Resultado de búsqueda", info)
                return
        
        messagebox.showinfo("No encontrado", "No se encontró un jurado con esa cédula")
    
    def buscar_votante(self):
        cedula = self.entry_buscar_votante.get().strip()
        
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula para buscar")
            return
        
        for (salon, mesa), votantes in self.datos["votantes"].items():
            for votante in votantes:
                if votante["cedula"] == cedula:
                    info = (
                        f"Votante encontrado:\n\n"
                        f"Nombre: {votante['nombre']}\n"
                        f"Cédula: {votante['cedula']}\n\n"
                        f"Asignado a:\n"
                        f"Salón {salon+1}, Mesa {mesa+1}"
                    )
                    
                    # Verificar asistencia
                    asistio = any(
                        a["cedula"] == cedula 
                        for a in self.datos["asistencia"] 
                        if a.get("salon") == f"Salón {salon+1}" 
                        and a.get("mesa") == f"Mesa {mesa+1}"
                    )
                    
                    info += f"\n\nAsistencia: {'Sí' if asistio else 'No'}"
                    
                    messagebox.showinfo("Resultado de búsqueda", info)
                    return
        
        messagebox.showinfo("No encontrado", "No se encontró un votante con esa cédula")
    
    def registrar_asistencia(self):
        top = tk.Toplevel(self.root)
        top.title("Registrar Asistencia")
        top.geometry("400x300")
        
        tk.Label(top, text="Cédula del votante:").pack()
        entry_cedula = tk.Entry(top)
        entry_cedula.pack()
        
        tk.Label(top, text="Salón:").pack()
        entry_salon = tk.Entry(top)
        entry_salon.pack()
        
        tk.Label(top, text="Mesa:").pack()
        entry_mesa = tk.Entry(top)
        entry_mesa.pack()
        
        tk.Label(top, text="Hora (HH:MM):").pack()
        entry_hora = tk.Entry(top)
        entry_hora.pack()
        
        def guardar():
            cedula = entry_cedula.get().strip()
            salon = entry_salon.get().strip()
            mesa = entry_mesa.get().strip()
            hora = entry_hora.get().strip()
            
            if not all([cedula, salon, mesa, hora]):
                messagebox.showwarning("Error", "Todos los campos son obligatorios")
                return
            
            # Validar formato de hora
            try:
                hora_dt = datetime.datetime.strptime(hora, "%H:%M").time()
                if hora_dt > datetime.time(16, 0):
                    messagebox.showerror("Error", "La hora no puede ser después de las 4:00 PM")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de hora inválido (use HH:MM)")
                return
            
            # Verificar que el votante existe
            votante_encontrado = False
            for (s, m), votantes in self.datos["votantes"].items():
                if f"Salón {s+1}" == salon and f"Mesa {m+1}" == mesa:
                    for v in votantes:
                        if v["cedula"] == cedula:
                            votante_encontrado = True
                            break
            
            if not votante_encontrado:
                messagebox.showerror("Error", "No se encontró el votante en la mesa especificada")
                return
            
            # Registrar asistencia
            self.datos["asistencia"].append({
                "cedula": cedula,
                "salon": salon,
                "mesa": mesa,
                "hora": hora
            })
            
            messagebox.showinfo("Éxito", "Asistencia registrada correctamente")
            top.destroy()
        
        tk.Button(top, text="Registrar", command=guardar).pack(pady=10)
    
    def cargar_resultados(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de resultados",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        try:
            if ruta.endswith('.json'):
                with open(ruta, 'r', encoding='utf-8') as file:
                    resultados = json.load(file)
            elif ruta.endswith('.csv'):
                with open(ruta, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    resultados = list(reader)
            else:
                messagebox.showerror("Error", "Formato de archivo no soportado")
                return
            
            # Validar y procesar resultados
            for res in resultados:
                # Validar estructura básica
                if 'salon' not in res or 'mesa' not in res or 'tarjeton' not in res:
                    raise ValueError("El archivo no tiene el formato correcto")
                
                # Validar respuestas (deben ser 9 preguntas)
                respuestas = []
                for i in range(1, 10):
                    key = f'p{i}' if f'p{i}' in res else f'respuesta_{i}'
                    if key not in res:
                        raise ValueError(f"Falta la pregunta {i}")
                    
                    respuesta = res[key].strip().capitalize()
                    if respuesta not in ['Sí', 'Si', 'S', 'No', 'N']:
                        raise ValueError(f"Respuesta inválida para pregunta {i}")
                    
                    # Estandarizar respuestas
                    respuestas.append('Sí' if respuesta in ['Sí', 'Si', 'S'] else 'No')
                
                # Agregar a los datos
                self.datos["resultados"].append({
                    "salon": res['salon'],
                    "mesa": res['mesa'],
                    "tarjeton": res['tarjeton'],
                    "respuestas": respuestas
                })
            
            messagebox.showinfo("Éxito", "Resultados cargados correctamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los resultados: {str(e)}")
    
    def guardar_configuracion(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar configuración",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        try:
            with open(ruta, 'w', encoding='utf-8') as file:
                json.dump(self.datos, file, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {str(e)}")
    
    def cargar_configuracion(self):
        ruta = filedialog.askopenfilename(
            title="Cargar configuración",
            filetypes=[("JSON files", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        try:
            with open(ruta, 'r', encoding='utf-8') as file:
                datos_cargados = json.load(file)
            
            # Validar estructura básica
            required_keys = ['configuracion', 'salones', 'jurados', 'votantes', 'asistencia', 'resultados', 'cedulas_registradas']
            if not all(key in datos_cargados for key in required_keys):
                raise ValueError("El archivo no contiene una configuración válida")
            
            self.datos = datos_cargados
            self.mostrar_botones()
            
            # Actualizar campos de entrada
            self.entry_sal.delete(0, tk.END)
            self.entry_sal.insert(0, str(self.datos["configuracion"]["salones"]))
            
            self.entry_mes.delete(0, tk.END)
            self.entry_mes.insert(0, str(self.datos["configuracion"]["mesas"]))
            
            self.entry_jur.delete(0, tk.END)
            self.entry_jur.insert(0, str(self.datos["configuracion"]["jurados"]))
            
            messagebox.showinfo("Éxito", "Configuración cargada correctamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la configuración: {str(e)}")
    
    def mostrar_resumen(self):
        if not self.datos["configuracion"]["salones"]:
            messagebox.showwarning("Advertencia", "Primero genere el centro de votación")
            return
        
        # Preparar datos para pandas
        data = {
            "Salón": [],
            "Total Jurados": [],
            "Jurados Registrados": [],
            "Total Votantes": [],
            "Votantes con Asistencia": [],
            "Mesas Completas": []
        }
        
        salones = self.datos["configuracion"]["salones"]
        mesas_por_salon = self.datos["configuracion"]["mesas"]
        jurados_por_mesa = self.datos["configuracion"]["jurados"]
        
        for s in range(salones):
            data["Salón"].append(f"Salón {s+1}")
            
            # Jurados
            total_jurados = mesas_por_salon * jurados_por_mesa
            data["Total Jurados"].append(total_jurados)
            
            jurados_registrados = sum(
                1 for key in self.datos["jurados"] 
                if key[0] == s
            )
            data["Jurados Registrados"].append(jurados_registrados)
            
            # Votantes
            total_votantes = sum(
                len(votantes) 
                for key, votantes in self.datos["votantes"].items() 
                if key[0] == s
            )
            data["Total Votantes"].append(total_votantes)
            
            # Asistencia
            votantes_con_asistencia = sum(
                1 for a in self.datos["asistencia"] 
                if a.get("salon") == f"Salón {s+1}"
            )
            data["Votantes con Asistencia"].append(votantes_con_asistencia)
            
            # Mesas completas
            mesas_completas = sum(
                1 for m in range(mesas_por_salon)
                if all((s, m, j) in self.datos["jurados"] for j in range(jurados_por_mesa))
            )
            data["Mesas Completas"].append(f"{mesas_completas}/{mesas_por_salon}")
        
        # Resumen de votación
        resumen_votacion = {}
        if self.datos["resultados"]:
            for i in range(9):
                resumen_votacion[f"P{i+1}"] = {
                    "Sí": sum(1 for r in self.datos["resultados"] if r["respuestas"][i] == "Sí"),
                    "No": sum(1 for r in self.datos["resultados"] if r["respuestas"][i] == "No")
                }
        
        # Crear ventana de resumen
        top = tk.Toplevel(self.root)
        top.title("Resumen Estadístico")
        top.geometry("800x600")
        
        # Frame para pandas
        frame_pandas = tk.Frame(top)
        frame_pandas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # Mostrar tabla
        text = tk.Text(frame_pandas)
        text.insert(tk.END, "Resumen por Salón:\n\n")
        text.insert(tk.END, df.to_string(index=False))
        
        if resumen_votacion:
            text.insert(tk.END, "\n\nResumen de Votación:\n\n")
            for pregunta, resultados in resumen_votacion.items():
                text.insert(tk.END, f"{pregunta}: Sí={resultados['Sí']}, No={resultados['No']}\n")
        
        text.pack(fill="both", expand=True)
    
    def generar_graficos(self):
        if not self.datos["configuracion"]["salones"]:
            messagebox.showwarning("Advertencia", "Primero genere el centro de votación")
            return
        
        # Crear ventana para gráficos
        top = tk.Toplevel(self.root)
        top.title("Gráficos Estadísticos")
        top.geometry("900x700")
        
        # Frame para gráficos
        frame_graficos = tk.Frame(top)
        frame_graficos.pack(fill="both", expand=True)
        
        # Preparar datos
        salones = [f"Salón {i+1}" for i in range(self.datos["configuracion"]["salones"])]
        
        # 1. Gráfico de barras: Jurados, Votantes y Asistencia por salón
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        
        jurados_registrados = [
            sum(1 for key in self.datos["jurados"] if key[0] == s)
            for s in range(self.datos["configuracion"]["salones"])
        ]
        
        total_votantes = [
            sum(len(v) for key, v in self.datos["votantes"].items() if key[0] == s)
            for s in range(self.datos["configuracion"]["salones"])
        ]
        
        votantes_asistencia = [
            sum(1 for a in self.datos["asistencia"] if a.get("salon") == f"Salón {s+1}")
            for s in range(self.datos["configuracion"]["salones"])
        ]
        
        width = 0.25
        x = range(len(salones))
        
        ax1.bar(x, jurados_registrados, width, label='Jurados Registrados')
        ax1.bar([i + width for i in x], total_votantes, width, label='Votantes Asignados')
        ax1.bar([i + 2*width for i in x], votantes_asistencia, width, label='Votantes con Asistencia')
        
        ax1.set_xticks([i + width for i in x])
        ax1.set_xticklabels(salones)
        ax1.set_title('Jurados, Votantes y Asistencia por Salón')
        ax1.legend()
        
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_graficos)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        
        # 2. Gráfico de pastel: Mesas completas vs incompletas
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        
        total_mesas = self.datos["configuracion"]["salones"] * self.datos["configuracion"]["mesas"]
        mesas_completas = sum(
            1 for s in range(self.datos["configuracion"]["salones"])
            for m in range(self.datos["configuracion"]["mesas"])
            if all((s, m, j) in self.datos["jurados"] 
                  for j in range(self.datos["configuracion"]["jurados"]))
        )
        
        labels = ['Mesas Completas', 'Mesas Incompletas']
        sizes = [mesas_completas, total_mesas - mesas_completas]
        
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        ax2.set_title('Proporción de Mesas Completas')
        
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_graficos)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        
        # 3. Gráfico de pastel: Asistencia de votantes
        if self.datos["votantes"]:
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            
            total_votantes = sum(len(v) for v in self.datos["votantes"].values())
            votantes_asistencia = len(self.datos["asistencia"])
            
            labels = ['Asistieron', 'No Asistieron']
            sizes = [votantes_asistencia, total_votantes - votantes_asistencia]
            
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax3.axis('equal')
            ax3.set_title('Asistencia de Votantes')
            
            canvas3 = FigureCanvasTkAgg(fig3, master=frame_graficos)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill="both", expand=True)
        
        # 4. Gráficos de barras horizontales por pregunta (si hay resultados)
        if self.datos["resultados"]:
            fig4, ax4 = plt.subplots(figsize=(8, 6))
            
            preguntas = [f"P{i+1}" for i in range(9)]
            si_counts = [
                sum(1 for r in self.datos["resultados"] if r["respuestas"][i] == "Sí")
                for i in range(9)
            ]
            no_counts = [
                sum(1 for r in self.datos["resultados"] if r["respuestas"][i] == "No")
                for i in range(9)
            ]
            
            y = range(len(preguntas))
            
            ax4.barh([i - 0.2 for i in y], si_counts, 0.4, label='Sí')
            ax4.barh([i + 0.2 for i in y], no_counts, 0.4, label='No')
            
            ax4.set_yticks(y)
            ax4.set_yticklabels(preguntas)
            ax4.set_xlabel('Número de Respuestas')
            ax4.set_title('Resultados por Pregunta')
            ax4.legend()
            
            canvas4 = FigureCanvasTkAgg(fig4, master=frame_graficos)
            canvas4.draw()
            canvas4.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CentroVotacion(root)
    root.mainloop()