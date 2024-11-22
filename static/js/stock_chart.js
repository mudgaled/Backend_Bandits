// static/js/stock_chart.js
function renderStockChart(priceHistory) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: priceHistory.map(data => data.date),
            datasets: [{
                label: 'Stock Price',
                data: priceHistory.map(data => data.price),
                borderColor: 'blue',
                fill: false,
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'Price ($)' } }
            }
        }
    });
}
