const express = require('express');
const bodyParser = require('body-parser');
const { PythonShell } = require('python-shell');
const path = require('path');
const NodeCache = require('node-cache');

const app = express();
const PORT = process.env.PORT || 4000;
const cache = new NodeCache({ stdTTL: 600 });

const publicDirectoryPath = path.join(__dirname, 'public');
const imageDirectoryPath = path.join(publicDirectoryPath, 'images');

let pngImagePath;
let svgImagePath;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(path.join(publicDirectoryPath, 'index.html'));
});

app.post('/generate_image', (req, res) => {
    try {
        const inputString1 = req.body.inputString1;
        const inputString2 = req.body.inputString2;
        const inputString3 = req.body.inputString3;

        const cacheKey = `${inputString1}_${inputString2}_${inputString3}`;
        const cachedImagePath = cache.get(cacheKey);

        if (cachedImagePath) {
            res.json({ imageUrl: cachedImagePath });
        } else {
            const options = {
                mode: 'text',
                pythonPath: 'python3',
                scriptPath: __dirname,
                args: [inputString1, inputString2, inputString3]
            };

            PythonShell.run('generate_image.py', options)
            .then(result => {
                const baseImagePath = result[0].trim();
                const imagePath = baseImagePath + '.png';

                pngImagePath = './public/' + baseImagePath + '.png';
                svgImagePath = './public/' + baseImagePath + '.svg';
                
                cache.set(cacheKey, imagePath);
                res.json({ imageUrl: imagePath });
            })
        }
    } catch (error) {
        console.error('Error generating image:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/download_png', (req, res) => {
    res.download(pngImagePath);
});

app.post('/download_svg', (req, res) => {
    res.download(svgImagePath);
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
