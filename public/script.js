document.getElementById('imageForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const inputString1 = document.querySelector('input[name="inputString1"]').value;
    const inputString2 = document.querySelector('input[name="inputString2"]').value;
    const inputString3 = document.querySelector('input[name="inputString3"]').value;

    fetch('/generate_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            inputString1: inputString1,
            inputString2: inputString2,
            inputString3: inputString3
        }),
    })
    .then(response => response.json())
    .then(data => {
        const imageUrl = data.imageUrl;
        const uniqueUrl = imageUrl + '?timestamp=' + new Date().getTime();
        document.getElementById('generatedImage').src = uniqueUrl;
        document.getElementById('formatSelection').style = '';
    })
    .catch(error => console.error('Error:', error));
});
