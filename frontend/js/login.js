document.getElementById("loginBtn").addEventListener("click", login);

async function login(){
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const errorMsg = document.getElementById("error");

    if(!email || !password) return errorMsg.innerText = "Please fill in all fields.";

    try{
        const data = await apiRequest("/login", "POST", {
            email: email,
            password: password
        });

        if(data.user){
            localStorage.setItem("userID", data.user.UserID);
            window.location.href = "dashboard.html";
        } else {
            errorMsg.innerText = data.error || "Invalid credentials";
        }
    } catch(err){
        console.error(err);
        errorMsg.innerText = "Server error. Please try again.";
    }
}