if(!localStorage.getItem("userID")){
    window.location.href = "login.html";
}

const userID = localStorage.getItem("userID");

async function loadBudgets(){
    try {
        const budgets = await apiRequest(`/budget/${userID}`);
        const tbody = document.querySelector("#budgetTable tbody");
        tbody.innerHTML = "";

        if (budgets && budgets.length > 0) {
            budgets.forEach(b => {
                const row = document.createElement("tr");

                // Determine dynamic color for status
                let statusColor = "#4C6FFF"; // Active
                if(b.Status === 'Warning') statusColor = "#ffa500";
                if(b.Status === 'Exceeded') statusColor = "#ff4c4c";
                if(b.Status === 'Finished') statusColor = "#A3AED0";

                row.innerHTML = `
                    <td style="color: ${statusColor}; font-weight: bold;">${b.Status}</td>
                    <td style="color: #A3AED0;">${b.LimitAmount}</td>
                    <td style="color: #4C6FFF;">${b.SpentAmount}</td>
                    <td style="color: #A3AED0; font-size: 0.85em;">
                        ${new Date(b.StartDate).toLocaleDateString()} - <br>${new Date(b.EndDate).toLocaleDateString()}
                    </td>
                    <td>
                        <button class="btn btn-edit" onclick="editBudget(${b.BudgetID}, ${b.LimitAmount}, ${b.SpentAmount})">Edit Limit</button>
                        <button class="btn btn-delete" onclick="deleteBudget(${b.BudgetID})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = "<tr><td colspan='5' style='text-align:center; color: #A3AED0; padding: 20px;'>No budgets found.</td></tr>";
        }
    } catch (err) {
        console.error("Error loading budgets:", err);
    }
}

async function createBudget(){
    const limitAmount = document.getElementById("limitAmount").value;
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    if(!limitAmount || !startDate || !endDate){
        return alert("Please fill in all fields.");
    }
    
    if(parseFloat(limitAmount) <= 0){
        return alert("Budget limit must be a positive number.");
    }

    // FRONTEND DATE VALIDATION
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    
    // Reset "today" to exactly midnight so it compares calendar days, not hours/minutes
    today.setHours(0, 0, 0, 0); 

    if (end < today) {
        return alert("End date cannot be in the past.");
    }
    if (end <= start) {
        return alert("End date must be after the start date.");
    }

    const response = await apiRequest("/budget", "POST", {
        user_id: userID,
        limit_amount: limitAmount,
        start_date: startDate,
        end_date: endDate
    });

    if(response.error) alert(response.error);
    else {
        document.getElementById("limitAmount").value = "";
        document.getElementById("startDate").value = "";
        document.getElementById("endDate").value = "";
        loadBudgets();
    }
}

async function editBudget(budgetID, currentLimit, spentAmount){
    const newLimit = prompt("Enter the new Budget Limit (INR):", currentLimit);
    if (newLimit === null || newLimit === "") return; 

    const parsedLimit = parseFloat(newLimit);

    // FRONTEND VALIDATION
    if (parsedLimit <= 0) {
        return alert("Budget limit must be a positive number.");
    }
    if (parsedLimit < spentAmount) {
        return alert(`Cannot set limit below your spent amount (${spentAmount} INR).`);
    }

    const response = await apiRequest(`/budget/${budgetID}`, "PUT", {
        limit_amount: parsedLimit
    });

    if(response.error) alert(response.error);
    else loadBudgets();
}

async function deleteBudget(budgetID){
    if(!confirm("Are you sure you want to delete this budget? All associated alerts will also be deleted.")) return;

    const response = await apiRequest(`/budget/${budgetID}`, "DELETE");

    if(response.error) alert(response.error);
    else loadBudgets();
}

// Initialize
loadBudgets();