function showSpinner() {
    document.querySelector('.spinner-container').style.display = 'block';
}

// Add a new function to handle form submission
async function downloadCatalog(event) {
    event.preventDefault();
    showSpinner();

    // Collect form data
    const formData = new FormData(event.target);
    const searchParams = new URLSearchParams();

    for (const [key, value] of formData.entries()) {
        searchParams.append(key, value);
    }

    // Send a request to the server
    const response = await fetch('/download_netflix_catalog', {
        method: 'POST',
        body: searchParams,
    });

    // Handle the server response
    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'catalog.xml';
        a.click();
        URL.revokeObjectURL(url);
    } else {
        // Handle any errors here
        console.error('Error downloading the file');
    }

    // Hide the spinner
    document.querySelector('.spinner-container').style.display = 'none';
}