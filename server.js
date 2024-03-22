const express = require('express');
const bodyParser = require('body-parser');
const { PythonShell } = require('python-shell');
const path = require('path');
const NodeCache = require('node-cache');
const findRemoveSync = require('find-remove');

// Create Express application
const app = express();

// Set up middleware (= functions accessing request and response objects)
app.use(bodyParser.urlencoded({ extended: true })); // Allow parsing URL-encoded payloads (= contents of message or request)
app.use(bodyParser.json()); // Allow parsing JSON payloads
app.use(express.static('public')); // Serve front-end files from public directory

// Set cache to last 10 mins
const cache = new NodeCache({ stdTTL: 600 }); // seconds

// Set route for home page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Set route at which handling POST request for generating images
app.post('/generate_image', (req, res) => {
    try {
        // Fetch input strings
        const { inputString1, inputString2, inputString3 } = req.body;
        // Create cache key based on input strings
        const cacheKey = `${inputString1}_${inputString2}_${inputString3}`;
        // Get path to cached image (empty if none)
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
                // Pull out image path and append '.png'
                const baseImagePath = result[0].trim();
                const imagePath = baseImagePath + '.png';
                
                // Cache and return path to image
                cache.set(cacheKey, imagePath);
                res.json({ imageUrl: imagePath });
            })
        }
    } catch (error) {
        console.error('Error making image:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Delete files once cache expires
setInterval(() => {
    findRemoveSync(path.join(__dirname, 'public', 'output'), {
        age: {seconds: 599},
        extensions: ['.png', '.svg'],
    });
    console.log("Emptied output image folder");
}, 600000); // millisecons

// Start server and listen for incoming requests at port
const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
