async function generateKey() {
  return await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
}

async function encryptFile(file, key) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const data = await file.arrayBuffer();

  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    data
  );

  return { encrypted, iv };
}

fetch("http://127.0.0.1:5000/me", { credentials: "include" })
.then(res => res.json())
.then(data => {
    if (!data.authenticated) {
        window.location.href = "login.html";
    } else {
        // Show the admin link only if the user is an admin
        if (data.is_admin) {
            document.getElementById("adminLink").style.display = "inline-block";
        }
    }
});

async function getDecryptionKey(password) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
    );
    return await crypto.subtle.deriveKey(
        { name: "PBKDF2", salt: enc.encode("cryptgo"), iterations: 100000, hash: "SHA-256" },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["decrypt"]
    );
}

async function downloadAndDecrypt(fileId, filename) {
    const password = prompt("Enter the decryption password:");
    if (!password) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/download/${fileId}`, { credentials: "include" });
        if (!res.ok) throw new Error("Download failed");
        
        const arrayBuffer = await res.arrayBuffer();
        const iv = arrayBuffer.slice(0, 12);
        const encryptedData = arrayBuffer.slice(12);

        const enc = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
        );
        const key = await crypto.subtle.deriveKey(
            { name: "PBKDF2", salt: enc.encode("cryptgo"), iterations: 100000, hash: "SHA-256" },
            keyMaterial, { name: "AES-GCM", length: 256 }, false, ["decrypt"]
        );

        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: new Uint8Array(iv) }, key, encryptedData
        );

        const blob = new Blob([decrypted]);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert("Wrong password or corrupted file.");
    }
}

async function deleteFile(fileId) {
    if (!confirm("Are you sure you want to delete this file?")) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/delete/${fileId}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (res.ok) {
            loadFiles(); 
        } else {
            alert("Delete failed.");
        }
    } catch (err) {
        alert("An error occurred.");
    }
}

document.getElementById("uploadBtn").onclick = async () => {
    const fileInput = document.getElementById("file");
    const password = document.getElementById("encPassword").value;

    if (!fileInput.files.length || !password) {
        alert("Please select a file and enter a password.");
        return;
    }

    const file = fileInput.files[0];
    
    try {
        const fileData = await file.arrayBuffer();
        
        const enc = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
        );
        const key = await crypto.subtle.deriveKey(
            { name: "PBKDF2", salt: enc.encode("cryptgo"), iterations: 100000, hash: "SHA-256" },
            keyMaterial, { name: "AES-GCM", length: 256 }, false, ["encrypt"]
        );

        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encrypted = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv }, key, fileData
        );

        const blob = new Blob([iv, new Uint8Array(encrypted)]);
        const formData = new FormData();
        formData.append("file", blob, file.name);

        const res = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            credentials: "include",
            body: formData
        });

        const data = await res.json();
        
        if (res.ok) {
            alert("File Uploaded Successfully!");
            loadFiles();
        } else {
            alert("Upload Failed: " + (data.error || "Unknown error"));
            if (res.status === 401) window.location.href = "login.html";
        }
    } catch (err) {
        alert("An error occurred during upload.");
    }
};

function loadFiles() {
    fetch("http://127.0.0.1:5000/files", { credentials: "include" })
    .then(res => res.json())
    .then(files => {
        const list = document.getElementById("fileList");
        list.innerHTML = ""; 

        if (!Array.isArray(files) || files.length === 0) {
            list.innerHTML = "<p style='text-align:center; color:#64748b;'>No files found.</p>";
            return;
        }

        files.forEach(f => {
    const li = document.createElement("li");
    li.className = "file-item";

    li.innerHTML = `
        <div class="file-info">
            <b>${f.filename}</b>
            <small>Encrypted on: ${f.uploaded_at}</small>
        </div>
        <div class="file-actions">
            <button class="download-btn">Download</button>
            <button class="delete-btn" style="background:#ef4444; margin-left:10px;">Delete</button>
        </div>
    `;

    li.querySelector(".download-btn").onclick = () => downloadAndDecrypt(f.id, f.filename);
    
    li.querySelector(".delete-btn").onclick = () => deleteFile(f.id);

    list.appendChild(li);
});
    })
    .catch(err => {});
}

loadFiles();

document.getElementById("togglePassword").addEventListener("change", function() {
    const passwordInput = document.getElementById("encPassword");
    if (this.checked) {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
});

document.getElementById("logout").onclick = () => {
  fetch("http://127.0.0.1:5000/logout", {
    method: "POST",
    credentials: "include"
  }).then(() => {
    window.location.href = "Cryptgo1.html";
  });
};