document.addEventListener("DOMContentLoaded", () => { // (DOM = Document Object Model, a programming interface for web documents)
    // Get references to index.html elements to change
    const generatedImage = document.getElementById('generatedImage');
    const formatSelection = document.getElementById('formatSelection');

    // Handle image generation
    document.getElementById('imageForm').addEventListener('submit', event => {
        event.preventDefault();
        // Extract input strings from form fields
        const inputStrings = Array.from(document.querySelectorAll('#imageForm input')).map(input => input.value);
        // Display loading state
        generatedImage.classList.add('loading');
        generatedImage.src = 'loader.gif';
        formatSelection.style = "display: none;" // Hide formatSelection
        // Send request to server to generate an image based on input strings
        fetch('/generate_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                inputString1: inputStrings[0],
                inputString2: inputStrings[1],
                inputString3: inputStrings[2]
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.imageUrl) {
                const imageUrl = data.imageUrl;
                const uniqueUrl = imageUrl + '?timestamp=' + new Date().getTime();
                generatedImage.classList.remove('loading');
                generatedImage.src = uniqueUrl;
                sessionStorage.setItem('imageUrl', imageUrl);
                // Show formatSelection after removing 'loading' class (takes ~ 150 ms)
                setTimeout(() => { formatSelection.style = ''; }, 150);
            } else {
                console.error('Unexpected response format:', data);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    function downloadPNG() {
        const storedImageUrl = sessionStorage.getItem('imageUrl');
        if (storedImageUrl) {
            fetch(storedImageUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to download PNG file');
                }
                return response.blob(); // Parse as Blob (= Binary Large Object, type for binary data in web browsers)
            })
            .then(blob => {
                // Create a temporary link to download the file
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mmàggini.png'; // Set name of downloaded file
                document.body.appendChild(a);
                a.click(); // Simulate click on the link to initiate download
                window.URL.revokeObjectURL(url);  // Release the object URL
                document.body.removeChild(a); // Delete the temporary link
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('No image URL available in session storage');
        }
    }

    function downloadSVG() {
        const storedImageUrl = sessionStorage.getItem('imageUrl');
        if (storedImageUrl) {
            fetch(storedImageUrl.replace(".png", ".svg")) // Extension is set to .png by default
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to download SVG file');
                }
                return response.blob(); // Parse as Blob (= Binary Large Object, type for binary data in web browsers)
            })
            .then(blob => {
                // Create a temporary link to download the file
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mmàggini.svg'; // Set name of downloaded file
                document.body.appendChild(a);
                a.click(); // Simulate click on the link to initiate download
                window.URL.revokeObjectURL(url);  // Release the object URL
                document.body.removeChild(a); // Delete the temporary link
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('No image URL available in session storage');
        }
    }

    // Attach event listeners to download buttons
    document.getElementById('downloadPNGButton').addEventListener('click', downloadPNG);
    document.getElementById('downloadSVGButton').addEventListener('click', downloadSVG);
});
