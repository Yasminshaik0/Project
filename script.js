const video = document.getElementById('video');
const startButton = document.getElementById('start-detection');
const blinkRateSpan = document.getElementById('blink-rate');
const alertMessageSpan = document.getElementById('alert-message');

// Access the user's camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error("Camera access denied:", error);
        alert("Please enable camera access to use this feature.");
    });

startButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');

    // Capture a frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frame = canvas.toDataURL('image/jpeg');

    // Send the frame to the backend for detection
    fetch('http://127.0.0.1:5000/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame })
    })
        .then(response => response.json())
        .then(data => {
            blinkRateSpan.textContent = `${data.blink_rate} blinks/min`;
            alertMessageSpan.textContent = data.alert;
        })
        .catch(error => {
            console.error('Error during detection:', error);
            alert("Error communicating with the backend.");
        });
});
