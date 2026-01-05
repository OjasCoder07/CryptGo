document.getElementById("otpForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const otp = document.getElementById("otp").value;

  fetch("http://127.0.0.1:5000/verify-otp", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ otp })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("message").innerText =
        data.message || data.error;

      if (data.message === "Login successful") {
        window.location.href = "dashboard.html";
      }
    })
    .catch(() => {
      document.getElementById("message").innerText = "Server error";
    });
});

