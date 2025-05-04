document.getElementById("json-file-input").addEventListener("change", function(event) {
    const file = event.target.files[0];
    if (file && file.type === "application/json") {
        const reader = new FileReader();

        reader.onload = function(e) {
            try {
                const jsonConfig = JSON.parse(e.target.result);
                createAndOpenPersonalizedWebsite(jsonConfig);
            } catch (error) {
                alert("Failed to parse JSON file. Please check the file format.");
                console.error("JSON Parse Error:", error);
            }
        };

        reader.onerror = function() {
            alert("Failed to read the file. Please try again.");
            console.error("File Read Error:", reader.error);
        };

        reader.readAsText(file);
    } else {
        alert("Please upload a valid JSON file.");
    }
});

function createAndOpenPersonalizedWebsite(config) {
    try {
        const newWindow = window.open();

        if (!newWindow) {
            throw new Error("Popup blocked by the browser. Please allow popups to generate the theme.");
        }

        const htmlContent = `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Personalized Website</title>
                <style>
                    body {
                        font-family: ${config.typography?.fontFamily || 'Arial, sans-serif'};
                        color: ${config.colorPalette?.textColor || '#000'};
                        background-color: ${config.colorPalette?.backgroundColor || '#fff'};
                    }
                    .layout {
                        display: ${config.layout?.type || 'block'};
                        gap: ${config.layout?.gap || '10px'};
                    }
                </style>
            </head>
            <body>
                <div class="layout">
                    <h1>Welcome to Your Personalized Website</h1>
                    <p>This is a dynamically generated page based on your JSON file.</p>
                </div>
            </body>
            </html>
        `;

        newWindow.document.write(htmlContent);
        newWindow.document.close();
    } catch (error) {
        alert("Failed to generate theme. Please check your DNA file.");
        console.error("Error Generating Theme:", error);
    }
}