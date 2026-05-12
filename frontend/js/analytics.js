if(!localStorage.getItem("userID")){
    window.location.href = "login.html";
}

const userID = localStorage.getItem("userID");

// Configure Chart.js for the Light Theme
Chart.defaults.color = '#A3AED0';
Chart.defaults.borderColor = '#E2E8F0';
Chart.defaults.font.family = "'Inter', sans-serif";

async function loadNetWorth(){
    try {
        const data = await apiRequest(`/analytics/networth/${userID}`);
        
        // Format as INR Currency
        const formatter = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });
        
        document.getElementById("netWorthTotal").innerText = formatter.format(data.TotalNetWorth);
        
        document.getElementById("netWorthBreakdown").innerHTML = `
            <span><strong>Wallet:</strong> ${formatter.format(data.Wallet)}</span> | 
            <span><strong>Bank:</strong> ${formatter.format(data.Bank)}</span> | 
            <span><strong>Crypto:</strong> ${formatter.format(data.Crypto)}</span>
        `;
    } catch (err) {
        console.error("Error loading net worth:", err);
        document.getElementById("netWorthTotal").innerText = "Error loading data";
    }
}

async function loadSpending(){
    try {
        const data = await apiRequest(`/analytics/${userID}`);
        const labels = data.map(d => d.CategoryName);
        const values = data.map(d => d.TotalSpent);

        const ctx = document.getElementById("spendingChart");
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Amount Spent (INR)",
                    data: values,
                    backgroundColor: "#4C6FFF", // Blue accent
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    } catch (err) {
        console.error("Error loading spending:", err);
    }
}

async function loadBudget(){
    try {
        const data = await apiRequest(`/analytics/budget/${userID}`);
        
        // Format labels using StartDate (e.g., "Budget (Mar 2026)")
        const labels = data.map(d => {
            const date = new Date(d.StartDate).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
            return `Budget (${date})`;
        });
        
        const spent = data.map(d => d.SpentAmount);
        const limits = data.map(d => d.LimitAmount);

        const ctx = document.getElementById("budgetChart");
        new Chart(ctx, {
            type: "bar", // Using a grouped bar chart to compare Spent vs Limit
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Amount Spent",
                        data: spent,
                        backgroundColor: "#ff4c4c", // Red for spent
                        borderRadius: 4
                    },
                    {
                        label: "Total Limit",
                        data: limits,
                        backgroundColor: "#E2E8F0", // Light grey for limit
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (err) {
        console.error("Error loading budget:", err);
    }
}

function initPage() {
    loadNetWorth();
    loadSpending();
    loadBudget();
}

initPage();