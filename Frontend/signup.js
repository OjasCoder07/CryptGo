console.log("signup.js loaded")

const form = document.getElementById("form")

form.addEventListener("submit", function(event) {

event.preventDefault()

const email = document.getElementById("email").value
const password = document.getElementById("password").value

fetch("http://127.0.0.1:5000/signup", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
email: email,
password: password
})
})
.then(response => response.json())
.then(data => {

document.getElementById("message").innerText =
data.message || data.error

})
.catch(error => {
document.getElementById("message").innerText = "Something went wrong"
})

})

