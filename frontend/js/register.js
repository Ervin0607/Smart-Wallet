document.getElementById("registerBtn").addEventListener("click", register);

async function register() {
    const name     = document.getElementById("regName").value.trim();
    const email    = document.getElementById("regEmail").value.trim();
    const phone    = document.getElementById("regPhone").value.trim();
    const account  = document.getElementById("regAccount").value.trim();
    const password = document.getElementById("regPassword").value;
    const errorMsg = document.getElementById("regError");

    errorMsg.innerText = "";
    errorMsg.style.color = "#ff4c4c";

    if (!name || !email || !password || !account) {
        return errorMsg.innerText = "Please fill in Name, Email, Password, and Account Number.";
    }

    try {
        const data = await apiRequest("/register", "POST", {
            name: name,
            email: email,
            phone: phone,
            account_number: account,
            password: password
        });

        if (data.message === "User registered successfully") {
            errorMsg.style.color = "#2ecc71";
            errorMsg.innerText = "Account created! Redirecting to login...";
            setTimeout(() => { window.location.href = "login.html"; }, 1500);
        } else {
            errorMsg.innerText = data.error || "Registration failed. Please try again.";
        }

    } catch (err) {
        console.error(err);
        errorMsg.innerText = "Server error. Please try again.";
    }
}
