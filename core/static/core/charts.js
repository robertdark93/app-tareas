// Charts for summary.html and admin/dashboard.html
// Requires Chart.js loaded globally and canvas elements in the DOM.
// All data is expected to be injected via data-* attributes or global JS variables.

// ── Summary page charts (summary.html) ──

function initSummaryCharts() {
    // Data expected to be set on window or via data attributes:
    //   window.chartData = {
    //       prioridad_labels: [...],
    //       prioridad_data: [...],
    //       dias_mes: 30,
    //       tareas_por_dia: [...]
    //   }

    const chartPrioridad = document.getElementById('chartPrioridad');
    const chartDias = document.getElementById('chartDias');
    if (!chartPrioridad || !chartDias) return;

    const colores = {
        urgente: '#f85149', alta: '#d29922', media: '#58a6ff', baja: '#3fb950',
        pendiente: '#d29922', proceso: '#58a6ff', revision: '#bc8cff', terminada: '#3fb950',
    };

    new Chart(chartPrioridad, {
        type: 'doughnut',
        data: {
            labels: window.chartData?.prioridad_labels || [],
            datasets: [{
                data: window.chartData?.prioridad_data || [],
                backgroundColor: [colores.urgente, colores.alta, colores.media, colores.baja],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { color: '#8b949e' } } }
        }
    });

    new Chart(chartDias, {
        type: 'bar',
        data: {
            labels: Array.from({length: window.chartData?.dias_mes || 30}, (_, i) => i + 1),
            datasets: [{
                label: 'Tareas creadas',
                data: window.chartData?.tareas_por_dia || [],
                backgroundColor: '#58a6ff',
                borderRadius: 3,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#8b949e' }, grid: { color: '#30363d' } },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } }
            }
        }
    });
}

// ── Admin dashboard charts (admin/dashboard.html) ──

function initAdminCharts() {
    // Data expected to be set on window:
    //   window.adminChartData = {
    //       tareas_por_usuario_labels: [...],
    //       tareas_por_usuario_data: [...],
    //       depto_labels: [...],
    //       depto_data: [...],
    //       monthly_labels: [...],
    //       monthly_created: [...],
    //       monthly_completed: [...],
    //       radar_labels: [...],
    //       radar_datasets: [...],
    //       stacked_labels: [...],
    //       stacked_pendientes: [...],
    //       stacked_proceso: [...],
    //       stacked_revision: [...],
    //       stacked_terminadas: [...]
    //   }

    const chartUsuarios = document.getElementById('chartUsuarios');
    if (!chartUsuarios) return;

    const colors = ['#58a6ff','#3fb950','#d29922','#f85149','#bc8cff','#39d2c0','#f0883e','#79c0ff'];
    const d = window.adminChartData || {};

    new Chart(chartUsuarios, {
        type: 'bar',
        data: {
            labels: d.tareas_por_usuario_labels || [],
            datasets: [{
                label: 'Tareas',
                data: d.tareas_por_usuario_data || [],
                backgroundColor: colors.slice(0, (d.tareas_por_usuario_labels || []).length),
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1, color: '#8b949e' }, grid: { color: '#30363d' } },
                x: { ticks: { color: '#8b949e' }, grid: { display: false } }
            }
        }
    });

    const chartDeptos = document.getElementById('chartDeptos');
    if (chartDeptos && d.depto_labels?.length) {
        new Chart(chartDeptos, {
            type: 'doughnut',
            data: {
                labels: d.depto_labels || [],
                datasets: [{
                    data: d.depto_data || [],
                    backgroundColor: colors,
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#8b949e' } } }
            }
        });
    }

    const chartMonthlyTrend = document.getElementById('chartMonthlyTrend');
    if (chartMonthlyTrend) {
        new Chart(chartMonthlyTrend, {
            type: 'line',
            data: {
                labels: d.monthly_labels || [],
                datasets: [
                    {
                        label: 'Creadas',
                        data: d.monthly_created || [],
                        borderColor: '#58a6ff',
                        backgroundColor: '#58a6ff33',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: '#58a6ff',
                    },
                    {
                        label: 'Completadas',
                        data: d.monthly_completed || [],
                        borderColor: '#3fb950',
                        backgroundColor: '#3fb95033',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: '#3fb950',
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#8b949e' } } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1, color: '#8b949e' }, grid: { color: '#30363d' } },
                    x: { ticks: { color: '#8b949e' }, grid: { display: false } }
                }
            }
        });
    }

    const chartRadar = document.getElementById('chartRadar');
    if (chartRadar && d.radar_datasets?.length) {
        new Chart(chartRadar, {
            type: 'radar',
            data: {
                labels: d.radar_labels || [],
                datasets: d.radar_datasets.map(ds => ({
                    label: ds.label,
                    data: ds.data,
                    borderColor: ds.color,
                    backgroundColor: ds.color + '22',
                    pointBackgroundColor: ds.color,
                    pointRadius: 4,
                }))
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#8b949e' } } },
                scales: {
                    r: {
                        grid: { color: '#30363d' },
                        ticks: { color: '#8b949e', backdropColor: 'transparent' },
                        angleLines: { color: '#30363d' },
                        pointLabels: { color: '#8b949e' },
                    }
                }
            }
        });
    }

    const chartStacked = document.getElementById('chartStacked');
    if (chartStacked && d.stacked_labels?.length) {
        new Chart(chartStacked, {
            type: 'bar',
            data: {
                labels: d.stacked_labels || [],
                datasets: [
                    {
                        label: 'Pendientes',
                        data: d.stacked_pendientes || [],
                        backgroundColor: '#d29922',
                        borderRadius: 2,
                    },
                    {
                        label: 'En Proceso',
                        data: d.stacked_proceso || [],
                        backgroundColor: '#58a6ff',
                        borderRadius: 2,
                    },
                    {
                        label: 'En Revisión',
                        data: d.stacked_revision || [],
                        backgroundColor: '#bc8cff',
                        borderRadius: 2,
                    },
                    {
                        label: 'Terminadas',
                        data: d.stacked_terminadas || [],
                        backgroundColor: '#3fb950',
                        borderRadius: 2,
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#8b949e' } } },
                scales: {
                    x: { stacked: true, ticks: { color: '#8b949e' }, grid: { display: false } },
                    y: { stacked: true, beginAtZero: true, ticks: { stepSize: 1, color: '#8b949e' }, grid: { color: '#30363d' } }
                }
            }
        });
    }
}
