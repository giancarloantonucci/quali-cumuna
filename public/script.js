document.getElementById('imageForm').addEventListener('submit', function (event) {
    event.preventDefault();
    
    const inputStrings = Array.from(document.querySelectorAll('#imageForm input')).map(input => input.value);

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
            document.getElementById('generatedImage').src = uniqueUrl;
            document.getElementById('formatSelection').style = '';
            sessionStorage.setItem('imageUrl', imageUrl);
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
            return response.blob();
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mmàggini.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => console.error('Error:', error));
    } else {
        console.error('No image URL available in session storage');
    }
}

function downloadSVG() {
    const storedImageUrl = sessionStorage.getItem('imageUrl');
    if (storedImageUrl) {
        fetch(storedImageUrl.replace(".png", ".svg"))
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to download SVG file');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a temporary link to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mmàggini.svg';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => console.error('Error:', error));
    } else {
        console.error('No image URL available in session storage');
    }
}

document.getElementById('downloadPNGButton').addEventListener('click', downloadPNG);
document.getElementById('downloadSVGButton').addEventListener('click', downloadSVG);
