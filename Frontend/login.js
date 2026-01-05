console.log("login.js loaded");

const form = document.getElementById("loginForm");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch("http://127.0.0.1:5000/login", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
  document.getElementById("message").innerText =
    data.message || data.error;

  if (data.otp) {
    alert("Your OTP is: " + data.otp);
  }

  if (data.message === "OTP generated") {
    window.location.href = "otp.html";
  }
})  
    .catch(() => {
      document.getElementById("message").innerText = "Server error";
    });
});

