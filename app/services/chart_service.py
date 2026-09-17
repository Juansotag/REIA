"""
Servicio de Analítica y Gráficas Headless para REIA.
GovLab: Universidad de la Sabana.
Genera diagramas de líneas individuales y diagramas de cajas y bigotes (boxplots) con medias
con la paleta de colores institucional UniSabana para la web, Word (.docx) y PDF.
"""

import io
import base64
from typing import Dict, Any, List
import matplotlib
matplotlib.use("Agg")  # Modo headless sin GUI
import matplotlib.pyplot as plt
import numpy as np

# Colores Institucionales UniSabana
C_BLUE_DARK = "#00135B"
C_BLUE_LIGHT = "#00387D"
C_YELLOW = "#f8a719"
C_RED = "#96272D"
C_BLUE_TINT = "#D9E1EF"
C_CREAM = "#F7EFD9"
PALETA_DIMENSIONES = ["#00135B", "#00387D", "#f8a719", "#2b8d04", "#96272D", "#6a1b9a"]

class ChartService:

    @staticmethod
    def generar_grafica_individual_base64(
        fechas: List[str],
        series_dimensiones: Dict[str, List[float]],
        nombre_rubrica: str = "Evolución de Rúbrica"
    ) -> str:
        """
        Genera una gráfica de líneas para un estudiante individual.
        X = tiempo, Y = calificaciones (0.0 a 5.0).
        Retorna la imagen en formato base64 PNG lista para incrustar en HTML o Word.
        """
        fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fcfdfd")

        # Configurar límites de calificación según escala nacional colombiana
        ax.set_ylim(0.0, 5.2)
        ax.set_yticks([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        ax.set_ylabel("Calificación (0.0 - 5.0)", fontsize=10, fontweight="bold", color=C_BLUE_DARK)
        ax.set_xlabel("Tiempo / Observaciones", fontsize=10, fontweight="bold", color=C_BLUE_DARK)
        ax.set_title(f"{nombre_rubrica} : Evolución Temporal", fontsize=12, fontweight="bold", color=C_BLUE_DARK, pad=12)

        # Franjas de tramos de desempeño (Decreto 1290)
        ax.axhspan(0.0, 2.9, facecolor="#fde8e8", alpha=0.35, label="Bajo (0.0 - 2.9)")
        ax.axhspan(3.0, 3.9, facecolor="#fff9e6", alpha=0.35, label="Básico (3.0 - 3.9)")
        ax.axhspan(4.0, 4.5, facecolor="#e8f4fd", alpha=0.35, label="Alto (4.0 - 4.5)")
        ax.axhspan(4.6, 5.0, facecolor="#eafaf1", alpha=0.35, label="Superior (4.6 - 5.0)")

        # Dibujar líneas por cada dimensión
        for idx, (dim_nombre, valores) in enumerate(series_dimensiones.items()):
            color = PALETA_DIMENSIONES[idx % len(PALETA_DIMENSIONES)]
            x_indices = list(range(len(valores)))
            ax.plot(
                x_indices,
                valores,
                marker="o",
                markersize=6,
                linewidth=2.2,
                color=color,
                label=dim_nombre,
                zorder=5
            )
            # Etiquetas numéricas en puntos
            for x, y in zip(x_indices, valores):
                ax.annotate(
                    f"{y:.1f}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 7),
                    ha="center",
                    fontsize=8,
                    fontweight="bold",
                    color=color
                )

        ax.set_xticks(range(len(fechas)))
        ax.set_xticklabels(fechas, rotation=25, ha="right", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.4, color="#cccccc")
        ax.legend(loc="lower right", fontsize=8, framealpha=0.9)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    @staticmethod
    def generar_grafica_agregada_curso_base64(
        periodos: List[str],
        distribuciones: List[List[float]],
        nombre_rubrica: str = "Rúbrica Agregada de Curso"
    ) -> str:
        """
        Genera una gráfica con Diagramas de Cajas y Bigotes (Boxplots) y línea punteada de la Media
        para mostrar la distribución estadística (mínimo, Q1, mediana, Q3, máximo) de un grupo/curso.
        """
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=150)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#fcfdfd")

        ax.set_ylim(0.0, 5.2)
        ax.set_yticks([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        ax.set_ylabel("Calificación (0.0 - 5.0)", fontsize=10, fontweight="bold", color=C_BLUE_DARK)
        ax.set_xlabel("Período / Hito Temporal", fontsize=10, fontweight="bold", color=C_BLUE_DARK)
        ax.set_title(f"{nombre_rubrica} : Distribución Grupal y Cuartiles", fontsize=12, fontweight="bold", color=C_BLUE_DARK, pad=12)

        # Franjas institucionales
        ax.axhspan(0.0, 2.9, facecolor="#fde8e8", alpha=0.3)
        ax.axhspan(3.0, 3.9, facecolor="#fff9e6", alpha=0.3)
        ax.axhspan(4.0, 4.5, facecolor="#e8f4fd", alpha=0.3)
        ax.axhspan(4.6, 5.0, facecolor="#eafaf1", alpha=0.3)

        # Crear Boxplots
        positions = list(range(1, len(periodos) + 1))
        bp = ax.boxplot(
            distribuciones,
            positions=positions,
            patch_artist=True,
            widths=0.45,
            showmeans=False,
            boxprops=dict(facecolor=C_BLUE_TINT, color=C_BLUE_DARK, linewidth=1.5),
            capprops=dict(color=C_BLUE_DARK, linewidth=1.5),
            whiskerprops=dict(color=C_BLUE_DARK, linewidth=1.2, linestyle="--"),
            flierprops=dict(marker="o", markerfacecolor=C_RED, markersize=4, linestyle="none"),
            medianprops=dict(color=C_YELLOW, linewidth=2.5)
        )

        # Calcular y trazar línea punteada de la Media Aritmética
        medias = [float(np.mean(d)) if len(d) > 0 else 0.0 for d in distribuciones]
        ax.plot(
            positions,
            medias,
            color=C_BLUE_LIGHT,
            linestyle=":",
            linewidth=2.4,
            marker="D",
            markersize=6,
            label="Media Aritmética Grupal",
            zorder=6
        )

        # Anotar valores de la media
        for x, m in zip(positions, medias):
            ax.annotate(
                f"x̄={m:.2f}",
                (x, m),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=8,
                fontweight="bold",
                color=C_BLUE_DARK
            )

        ax.set_xticks(positions)
        ax.set_xticklabels(periodos, rotation=20, ha="right", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.4, color="#cccccc")
        ax.legend(loc="lower right", fontsize=8, framealpha=0.9)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
