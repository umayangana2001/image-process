<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>People Counter Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .counts { font-size: 20px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>People Counter Dashboard</h1>

    <div class="counts">
        <p>Current In: {{ count_in }}</p>
        <p>Current Out: {{ count_out }}</p>
    </div>

    <canvas id="peopleChart" width="800" height="400"></canvas>

    <script>
        const labels = {{ chart_labels|tojson }};
        const data = {
            labels: labels,
            datasets: [
                {
                    label: 'Count In',
                    data: {{ chart_data['count_in']|tojson }},
                    borderColor: 'green',
                    backgroundColor: 'rgba(0, 255, 0, 0.2)',
                    fill: true
                },
                {
                    label: 'Count Out',
                    data: {{ chart_data['count_out']|tojson }},
                    borderColor: 'red',
                    backgroundColor: 'rgba(255, 0, 0, 0.2)',
                    fill: true
                }
            ]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'People Flow Over Time' }
                }
            }
        };

        new Chart(document.getElementById('peopleChart'), config);
    </script>
</body>
</html>
