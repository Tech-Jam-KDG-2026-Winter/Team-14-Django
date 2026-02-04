document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/history/') 
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) return;

            // APIのフィールド名に合わせて取得
            const dates = data.map(item => item.date);
            const steps = data.map(item => item.step_count); // 歩数
            const scores = data.map(item => item.calculated_value); // 習慣化スコア

            const ctx = document.getElementById('stepChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [{
                        label: '歩数',
                        data: steps,
                        backgroundColor: '#4CAF50',
                        borderRadius: 5,
                        yAxisID: 'y' // 左側の軸を使用
                    },
                    {
                        label: '習慣化スコア',
                        data: scores,
                        type: 'line', // スコアはラインで見せると分かりやすい
                        borderColor: '#FF5722',
                        backgroundColor: '#FF5722',
                        yAxisID: 'y1' // 右側の軸を使用（単位が異なるため）
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: '歩数' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: { drawOnChartArea: false }, // グリッドの重なりを防ぐ
                            title: { display: true, text: 'スコア' }
                        }
                    }
                }
            });

            // 合計スコアの計算と表示
            const total = scores.reduce((a, b) => a + b, 0);
            const totalElement = document.getElementById('total-score');
            if (totalElement) {
                totalElement.innerText = total.toFixed(1);
            }
        })
        .catch(err => console.error("APIエラー:", err));
});