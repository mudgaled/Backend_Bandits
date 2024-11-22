// Function to fetch historical stock data from the backend
async function fetchStockData(ticker) {
    const response = await fetch(`/stocks/history?ticker=${ticker}`);
    const data = await response.json();
    return data;
}

// Function to render a line chart with the fetched stock data
async function renderChart(ticker) {
    const stockData = await fetchStockData(ticker);

    const labels = stockData.dates;  // x-axis values (e.g., dates)
    const prices = stockData.prices; // y-axis values (e.g., prices)

    const ctx = document.getElementById('priceChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${ticker} Stock Price`,
                data: prices,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price (USD)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Call renderChart function with the ticker symbol
// This ticker can be dynamically set or passed as a parameter
document.addEventListener('DOMContentLoaded', () => {
    const ticker = document.getElementById('priceChart').getAttribute('data-ticker');
    renderChart(ticker);
});
