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
        } else {
            console.error('Unexpected response format:', data);
        }
    })
    .catch(error => console.error('Error:', error));
});
