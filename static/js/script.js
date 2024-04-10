document.getElementById('encryptionForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var formData = new FormData(this);
    fetch('/encrypt', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        document.getElementById('encryptionResult').innerText = result;
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('decryptionForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var formData = new FormData(this);
    fetch('/decrypt', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        document.getElementById('decryptionResult').innerText = result;
    })
    .catch(error => console.error('Error:', error));
});
