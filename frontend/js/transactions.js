if(!localStorage.getItem("userID")){
    window.location.href = "login.html";
}

const userID = localStorage.getItem("userID");
let walletID = null; 

async function initPage(){
    try {
        const wallet = await apiRequest(`/wallet/${userID}`);
        if(wallet && wallet.WalletID){
            walletID = wallet.WalletID; 
            loadTransactions(); 
        }
    } catch (err) {
        console.error("Error loading wallet:", err);
    }
}


async function loadTransactions(){
    try {
        const txns = await apiRequest(`/transactions/${walletID}`);
        const tbody = document.querySelector("#txnTable tbody");
        tbody.innerHTML = "";

        if (txns && txns.length > 0) {
            txns.forEach(t => {
                const row = document.createElement("tr");

                // Determine dynamic color for status
                let statusColor = "#A3AED0"; // Default grey
                if(t.Status && t.Status.toUpperCase() === 'COMPLETED') statusColor = "#22C55E"; // Green
                else if(t.Status && t.Status.toUpperCase() === 'PENDING') statusColor = "#ffa500"; // Orange
                else if(t.Status && t.Status.toUpperCase() === 'FAILED') statusColor = "#ff4c4c"; // Red

                row.innerHTML = `
                    <td style="color: #A3AED0;">#${t.TransactionID}</td>
                    <td>${t.CategoryName}</td>
                    <td style="color: #4C6FFF; font-weight: bold;">${t.Amount}</td>
                    <td>
                        <span style="background: #EEF2FF; color: #4C6FFF; padding: 4px 10px; border-radius: 8px; font-size: 0.85em; font-weight: 500;">
                            ${t.PaymentMode}
                        </span>
                    </td>
                    <td style="color: #A3AED0;">${new Date(t.TransactionDate).toLocaleString()}</td>
                    <td style="color: ${statusColor}; font-weight: bold;">${t.Status ? t.Status.toUpperCase() : 'UNKNOWN'}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = "<tr><td colspan='6' style='text-align:center; color: #A3AED0; padding: 20px;'>No transactions found.</td></tr>";
        }

    } catch (err) {
        document.querySelector("#txnTable tbody").innerHTML = "<tr><td colspan='6' style='color:#ff4c4c;'>Error loading transactions.</td></tr>";
        console.error("Transaction error:", err);
    }
}

async function createTransaction(force = false){
    
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;

    if(!amount || amount <= 0) return alert("Please enter a valid amount.");

    const response = await apiRequest("/transaction", "POST", {
        wallet_id: walletID, // Now this works perfectly
        category_id: category,
        amount: amount,
        force: force 
    });

    if(response.error) {
        alert(response.error);
    } 
    else if (response.warning) {
        const proceed = confirm(response.message);
        
        if (proceed) {
            createTransaction(true);
        } else {
            console.log("Transaction cancelled by user to save budget.");
        }
    } 
    else {
        document.getElementById("amount").value = "";
        loadTransactions(); // Now this works perfectly without passing arguments
    }
}

// Trigger the initialization
initPage();