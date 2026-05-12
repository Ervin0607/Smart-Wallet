if(!localStorage.getItem("userID")){
    window.location.href = "login.html";
}

const userID = localStorage.getItem("userID");

async function loadDashboard(){
    try {
        // 1. Load Wallet Balance
        const wallet = await apiRequest(`/wallet/${userID}`);
        document.getElementById("balance").innerText = `${wallet.Balance} ${wallet.Currency}`;

        // 2. Load Bank Accounts
        const bankAccounts = await apiRequest(`/bankaccount/${userID}`);
        const bankDiv = document.getElementById("bankAccounts");
        bankDiv.innerHTML = "";
        
        if (bankAccounts && bankAccounts.length > 0) {
            bankAccounts.forEach(acc => {
                bankDiv.innerHTML += `
                <div class="bank-item">
                    <div style="color: #4C6FFF; font-weight: bold;">${acc.BankName}</div>
                    <div style="font-size: 0.85em; color: #A3AED0; margin-bottom: 5px;">Acct ending in ${acc.AccountNumber.slice(-4)}</div>
                    <div>${acc.BankBalance} INR</div>
                </div>`;
            });
        } else {
            bankDiv.innerHTML = "<p>No linked bank accounts.</p>";
        }

        // 3. Load Budgets List (Now expecting an array from the updated backend)
        const budgets = await apiRequest(`/budget/${userID}`);
        const budgetDiv = document.getElementById("budgetsList");
        budgetDiv.innerHTML = "";
        
        if (budgets && budgets.length > 0) {
            budgets.forEach(b => {
                // Calculate percentage for progress bar
                const percent = Math.min(100, (b.SpentAmount / b.LimitAmount) * 100).toFixed(1);
                
                // Determine color based on usage
                let colorClass = "progress-fill";
                if (percent >= 100) colorClass += " danger";
                else if (percent >= 80) colorClass += " warning";

                budgetDiv.innerHTML += `
                    <div class="budget-item">
                        <div class="budget-header">
                            <span>Status: ${b.Status}</span>
                            <span>${b.SpentAmount} / ${b.LimitAmount}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="${colorClass}" style="width: ${percent}%"></div>
                        </div>
                        <div style="font-size: 0.8em; color: #A3AED0; margin-top: 5px; text-align: right;">
                            ${percent}% Used
                        </div>
                    </div>
                `;
            });
        } else {
            budgetDiv.innerHTML = "<p>No active budgets.</p>";
        }

        // 4. Load Alerts
        const alerts = await apiRequest(`/alerts/${userID}`);
        const list = document.getElementById("alerts");
        list.innerHTML = "";
        
        if (alerts && alerts.length > 0) {
            alerts.slice(0, 3).forEach(a => { // Show top 3 alerts
                const li = document.createElement("li");
                li.innerHTML = `<strong>${a.AlertMessage}</strong><br><span style="font-size:0.8em; color:#A3AED0">${new Date(a.TriggerDate).toLocaleDateString()}</span>`;
                list.appendChild(li);
            });
        } else {
            list.innerHTML = "<li style='border:none; background:none;'>No active alerts.</li>";
        }

        // 5. Load Recent Transactions
        const txns = await apiRequest(`/transactions/${wallet.WalletID}`);
        const tbody = document.querySelector("#recentTxns tbody");
        tbody.innerHTML = "";
        
        if (txns && txns.length > 0) {
            txns.slice(0, 5).forEach(t => {
                const row = document.createElement("tr");
                row.innerHTML = `
                <td>#${t.TransactionID}</td>
                <td style="color: #4C6FFF; font-weight: bold;">${t.Amount}</td>
                <td>${new Date(t.TransactionDate).toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = "<tr><td colspan='3'>No recent transactions.</td></tr>";
        }

    } catch (error) {
        console.error("Failed to load dashboard:", error);
    }
}

// Initialize
loadDashboard();