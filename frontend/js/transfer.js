document.addEventListener("DOMContentLoaded", function() {
    console.log("Transfer.js loaded successfully.");

    const payNowBtn = document.getElementById('payNowBtn');
    const confirmPayBtn = document.getElementById('confirmPayBtn');
    const cancelTransferBtn = document.getElementById('cancelTransferBtn');
    const authModalOverlay = document.getElementById('authModalOverlay');
    const modalAmountText = document.getElementById('modalAmountText');
    const authForm = document.getElementById('authForm');
    const paymentVia = document.getElementById('paymentVia');
    const cryptoSelectionGroup = document.getElementById('cryptoSelectionGroup');
    const cryptoAssetId = document.getElementById('cryptoAssetId');

    let senderWalletId = null;
    const userID = localStorage.getItem("userID");
    if(userID) {
        apiRequest(`/wallet/${userID}`).then(w => {
            if(w && w.WalletID) senderWalletId = w.WalletID;
        }).catch(err => console.error(err));
    }

    if (paymentVia) {
        paymentVia.addEventListener('change', async function() {
            if (this.value === 'crypto') {
                cryptoSelectionGroup.style.display = 'block';
                if (!senderWalletId) return alert("Wallet not loaded yet. Please wait a moment.");
                try {
                    const assets = await apiRequest(`/crypto/${senderWalletId}`);
                    cryptoAssetId.innerHTML = '<option value="">Select a token...</option>';
                    if (assets && assets.length > 0) {
                        assets.forEach(a => {
                            cryptoAssetId.innerHTML += `<option value="${a.AssetID}">${a.CryptoName} (${a.Symbol}) - You own: ${a.Quantity}</option>`;
                        });
                    } else {
                        cryptoAssetId.innerHTML = '<option value="">No crypto assets available</option>';
                    }
                } catch(e) {
                    cryptoAssetId.innerHTML = '<option value="">Error loading assets</option>';
                }
            } else {
                cryptoSelectionGroup.style.display = 'none';
                cryptoAssetId.value = '';
            }
        });
    }

    // 1. OPEN THE MODAL
    if (payNowBtn) {
        payNowBtn.addEventListener('click', function(event) {
            event.preventDefault();

            const recipient_id = document.getElementById('accId').value;
            const amount = document.getElementById('amount').value;

            if (!recipient_id || !amount || amount <= 0) {
                alert("Please enter a valid Recipient ID and Amount.");
                return;
            }

            if (modalAmountText) {
                modalAmountText.innerText = `Please confirm your identity to send ₹${parseFloat(amount).toFixed(2)}`;
            }

            if (authModalOverlay) {
                authModalOverlay.style.display = 'flex';
            }
        });
    }

    // 2. CLOSE THE MODAL (Cancel Button)
    if (cancelTransferBtn) {
        cancelTransferBtn.addEventListener('click', function(event) {
            event.preventDefault();
            if (authModalOverlay) authModalOverlay.style.display = 'none';
            const passField = document.getElementById('authPassword');
            if (passField) passField.value = '';
        });
    }

    // 3. PREVENT 'ENTER' KEY FROM RELOADING THE PAGE
    if (authForm) {
        authForm.addEventListener('submit', function(event) {
            event.preventDefault(); 
            if (confirmPayBtn) confirmPayBtn.click(); 
        });
    }

    // 4. PROCESS THE PAYMENT
    if (confirmPayBtn) {
        confirmPayBtn.addEventListener('click', async function(event) {
            event.preventDefault();
            
            const sender_id = localStorage.getItem("userID");
            
            if (!sender_id) {
                alert("Session expired. Please log in again.");
                window.location.href = "login.html";
                return;
            }
            
            const recipient_id = document.getElementById('accId').value;
            const payment_via = document.getElementById('paymentVia').value;
            const amount = document.getElementById('amount').value;
            const password = document.getElementById('authPassword').value;
            
            // 🔥 NEW: Grab the Category ID! (Fallback to 1 if the HTML is missing)
            const catElement = document.getElementById('categoryId');
            const category_id = catElement ? catElement.value : 1;

            const assetElement = document.getElementById('cryptoAssetId');
            const asset_id = assetElement ? assetElement.value : null;

            if (payment_via === 'crypto' && !asset_id) {
                alert("Please select a crypto token to pay with.");
                return;
            }

            if (!password) {
                alert("Please enter your password to confirm.");
                return;
            }

            try {
                confirmPayBtn.innerText = "Processing...";
                confirmPayBtn.disabled = true;

                // First Attempt
                const response = await fetch('http://127.0.0.1:5000/transfer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sender_id: sender_id,
                        recipient_id: recipient_id,
                        payment_via: payment_via,
                        amount: amount,
                        password: password,
                        category_id: category_id,
                        asset_id: asset_id
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.warning) {
                        const proceedAnyway = confirm(data.message);
                        
                        if (proceedAnyway) {
                            confirmPayBtn.innerText = "Forcing Transfer...";
                            
                            const overrideResponse = await fetch('http://127.0.0.1:5000/transfer', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    sender_id: sender_id,
                                    recipient_id: recipient_id,
                                    payment_via: payment_via,
                                    amount: amount,
                                    password: password,
                                    category_id: category_id, // 🔥 Added here too!
                                    asset_id: asset_id,
                                    force: true 
                                })
                            });
                            
                            const errData = await overrideResponse.json();

                            if (overrideResponse.ok) {
                                alert("✅ Payment Successful (Budget Overridden)!");
                                window.location.href = "dashboard.html";
                            } else {
                                alert("❌ " + errData.error);
                            }
                        } else {
                            if (authModalOverlay) authModalOverlay.style.display = 'none';
                            const passField = document.getElementById('authPassword');
                            if (passField) passField.value = '';
                        }
                    } else {
                        alert("✅ Payment Successful!");
                        window.location.href = "dashboard.html";
                    }
                } else {
                    alert("❌ " + data.error);
                }

            } catch (error) {
                console.error("Network Fetch Error:", error);
                alert("❌ Network Error. Make sure the Flask server is running.");
            } finally {
                confirmPayBtn.innerText = "Verify & Pay";
                confirmPayBtn.disabled = false;
            }
        });
    }
});