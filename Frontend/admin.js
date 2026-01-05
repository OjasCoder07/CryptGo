fetch("http://127.0.0.1:5000/admin/logs", { credentials: "include" })
.then(res => {
    if (res.status === 403) {
        alert("Access Denied: Admins Only");
        window.location.href = "dashboard.html";
    }
    return res.json();
})
.then(logs => {
    const tableBody = document.getElementById("logBody");
    if (logs.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='4'>No logs found in the database.</td></tr>";
        return;
    }
    
    logs.forEach(log => {
        const row = `<tr>
            <td>${log.email}</td>
            <td><strong>${log.action}</strong></td>
            <td>${log.details}</td>
            <td>${log.timestamp}</td>
        </tr>`;
        tableBody.innerHTML += row;
    });
})
.catch(err => console.error("Error loading logs:", err));