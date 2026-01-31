// static/js/history.js
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/history/') 
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) return;

            const dates = data.map(item => item.date);
            const scores = data.map(item => item.score);

            const ctx = document.getElementById('stepChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [{
                        label: '習慣化スコア',
                        data: scores,
                        backgroundColor: '#4CAF50',
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            });

            const total = scores.reduce((a, b) => a + b, 0);
            document.getElementById('total-score').innerText = total.toFixed(1);
        })
        .catch(err => console.error("APIエラー:", err));
});