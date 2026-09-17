/**
 * charts.js - Graficos interactivos con Chart.js para REIA
 * GovLab - Universidad de la Sabana.
 */

let activeChartInstance = null;

function renderizarGraficaWeb(canvasId, configData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (activeChartInstance) {
        activeChartInstance.destroy();
    }

    const { tipo, labels, datasets, titulo } = configData;

    activeChartInstance = new Chart(ctx, {
        type: tipo || 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: !!titulo,
                    text: titulo,
                    font: { size: 14, weight: 'bold' },
                    color: '#00135B'
                },
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { size: 11 } }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 19, 91, 0.9)',
                    padding: 10,
                    titleFont: { size: 12, weight: 'bold' },
                    bodyFont: { size: 11 }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 5,
                    ticks: { stepSize: 1.0 },
                    title: {
                        display: true,
                        text: 'Calificación (0.0 - 5.0)',
                        color: '#00135B',
                        font: { weight: 'bold' }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Tiempo / Observaciones',
                        color: '#00135B',
                        font: { weight: 'bold' }
                    }
                }
            }
        }
    });
}
