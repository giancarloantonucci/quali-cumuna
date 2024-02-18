const express = require('express');
const bodyParser = require('body-parser');
const { PythonShell } = require('python-shell');

const app = express();
const PORT = process.env.PORT || 4000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

app.post('/generate_image', (req, res) => {
    const inputString1 = req.body.inputString1;
    const inputString2 = req.body.inputString2;
    const inputString3 = req.body.inputString3;

    let options = {
        mode: 'text',
        pythonPath: 'python3',
        scriptPath: __dirname,
        args: [inputString1, inputString2, inputString3]
    };

    PythonShell.run('generate_image.py', options).then(result => {
        const imagePath = result[0].trim();
        res.json({ imageUrl: imagePath });
    });
});

app.post('/download_png', (req, res) => {
    const file = __dirname + '/public/mmaggini.png';
    res.download(file);
});

app.post('/download_svg', (req, res) => {
    const file = __dirname + '/public/mmaggini.svg';
    res.download(file);
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
