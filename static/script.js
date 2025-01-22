function shuffleJob() {
    let responsibilities = document.getElementById("responsibilities").value;
    let jobDescription = document.getElementById("job_description").value;

    fetch("/shuffle", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            responsibilities: responsibilities,
            job_description: jobDescription
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("output").value = data.shuffled_result;
    })
    .catch(error => console.error("Error:", error));
}
