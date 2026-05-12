if(!localStorage.getItem("userID")){
    window.location.href = "login.html";
}

const userID = localStorage.getItem("userID");
let walletID = null;
let cryptoPrices = {}; // Store prices for quick calculation

async function initPage(){
    const wallet = await apiRequest(`/wallet/${userID}`);
    walletID = wallet.WalletID;

    await loadPricesAndDropdowns();
    await loadBankAccounts();
    await loadCryptoTable();
}

async function loadPricesAndDropdowns(){
    const assets = await apiRequest("/crypto/prices");
    const buySelect = document.getElementById("buyCryptoID");
    const sellSelect = document.getElementById("sellCryptoID");
    
    buySelect.innerHTML = "";
    sellSelect.innerHTML = "";

    assets.forEach(a => {
        cryptoPrices[a.CryptoID] = a.LiveMarketPrice; // Save price to dictionary
        
        const optionHTML = `<option value="${a.CryptoID}">${a.CryptoName} (${a.Symbol})</option>`;
        buySelect.innerHTML += optionHTML;
        sellSelect.innerHTML += optionHTML;
    });
}

async function loadBankAccounts(){
    const bankAccounts = await apiRequest(`/bankaccount/${userID}`);
    const bankSelect = document.getElementById("bankAccount");
    bankSelect.innerHTML = "";
    
    if(bankAccounts && bankAccounts.length > 0){
        bankAccounts.forEach(acc => {
            bankSelect.innerHTML += `<option value="${acc.AccountID}">
                ${acc.BankName} (...${acc.AccountNumber.slice(-4)}) - ${acc.BankBalance} INR
            </option>`;
        });
    } else {
        bankSelect.innerHTML = `<option value="">No Bank Linked</option>`;
    }
}

async function loadCryptoTable(){
    const assets = await apiRequest(`/crypto/${walletID}`);
    const tbody = document.querySelector("#cryptoTable tbody");
    tbody.innerHTML = "";

    if(assets && assets.length > 0) {
        assets.forEach(a => {
            const row = document.createElement("tr");
            row.innerHTML = `
            <td style="color: #4C6FFF; font-weight: bold;">${a.Symbol}</td>
            <td>${a.CryptoName}</td>
            <td>${a.Quantity}</td>
            <td style="color: #A3AED0;">${a.LiveMarketPrice} INR</td>
            `;
            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = "<tr><td colspan='4' style='text-align:center; color:#A3AED0;'>No assets owned.</td></tr>";
    }
}

// UI Interaction functions
function toggleBankSelect(){
    const mode = document.getElementById("paymentMode").value;
    // Updated this slightly to catch any variation of "Bank" just in case!
    document.getElementById("bankSelectGroup").style.display = mode.includes("Bank") ? "block" : "none";
}

function updateBuyCost(){
    const crypto_id = document.getElementById("buyCryptoID").value;
    const quantity = parseFloat(document.getElementById("buyQuantity").value) || 0;
    const price = cryptoPrices[crypto_id] || 0;
    document.getElementById("buyTotalCost").innerText = (price * quantity).toFixed(2) + " INR";
}

function updateSellRev(){
    const crypto_id = document.getElementById("sellCryptoID").value;
    const quantity = parseFloat(document.getElementById("sellQuantity").value) || 0;
    const price = cryptoPrices[crypto_id] || 0;
    document.getElementById("sellTotalRev").innerText = (price * quantity).toFixed(2) + " INR";
}

// Transaction functions
async function buyCrypto(force = false){
    const crypto_id = document.getElementById("buyCryptoID").value;
    const quantity = document.getElementById("buyQuantity").value;
    const payment_mode = document.getElementById("paymentMode").value;
    const account_id = document.getElementById("bankAccount").value;

    if(!quantity || quantity <= 0) return alert("Please enter a valid quantity.");

    const response = await apiRequest("/crypto/buy", "POST", {
        wallet_id: walletID,
        crypto_id: crypto_id,
        quantity: quantity,
        payment_mode: payment_mode,
        account_id: account_id, // THE FIX: Just pass it directly!
        force: force 
    });

    if(response.error) {
        alert(response.error);
    } 
    else if (response.warning) {
        const proceed = confirm(response.message);
        
        if (proceed) {
            buyCrypto(true);
        } else {
            console.log("Crypto purchase cancelled by user to save budget.");
        }
    } 
    else {
        document.getElementById("buyQuantity").value = "";
        updateBuyCost();
        loadCryptoTable();
    }
}

async function sellCrypto(){
    const crypto_id = document.getElementById("sellCryptoID").value;
    const quantity = document.getElementById("sellQuantity").value;

    if(!quantity || quantity <= 0) return alert("Please enter a valid quantity.");

    const response = await apiRequest("/crypto/sell", "POST", {
        wallet_id: walletID,
        crypto_id: crypto_id,
        quantity: quantity
    });

    if(response.error) alert(response.error);
    else {
        document.getElementById("sellQuantity").value = "";
        updateSellRev();
        loadCryptoTable();
    }
}

// Initialize
initPage();