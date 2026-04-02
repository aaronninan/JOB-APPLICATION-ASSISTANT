const resumeInput = document.getElementById("resume");
const jobDescriptionInput = document.getElementById("jobDescription");
const analyzeButton = document.getElementById("analyzeBtn");
const statusMessage = document.getElementById("statusMessage");

const missingSkillsList = document.getElementById("missingSkillsList");
const weakAreasList = document.getElementById("weakAreasList");
const suggestionsList = document.getElementById("suggestionsList");
const rawResponse = document.getElementById("rawResponse");


function renderList(element, items, emptyMessage) {
    element.innerHTML = "";

    if (!items || items.length === 0) {
        const listItem = document.createElement("li");
        listItem.className = "placeholder";
        listItem.textContent = emptyMessage;
        element.appendChild(listItem);
        return;
    }

    items.forEach((item) => {
        const listItem = document.createElement("li");
        listItem.textContent = item;
        element.appendChild(listItem);
    });
}


async function analyzeResume() {
    const resume = resumeInput.value.trim();
    const jobDescription = jobDescriptionInput.value.trim();

    if (!resume || !jobDescription) {
        statusMessage.textContent = "Please fill in both fields before analyzing.";
        return;
    }

    analyzeButton.disabled = true;
    statusMessage.textContent = "Analyzing resume with the AI agent...";

    renderList(missingSkillsList, [], "Analyzing missing skills...");
    renderList(weakAreasList, [], "Analyzing weak areas...");
    renderList(suggestionsList, [], "Generating suggestions...");
    rawResponse.textContent = "Waiting for agent response...";

    try {
        console.log("Sending user input to backend...");

        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                resume: resume,
                job_description: jobDescription,
            }),
        });

        const data = await response.json();
        console.log("Backend response:", data);

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong during analysis.");
        }

        renderList(
            missingSkillsList,
            data.missing_skills,
            "No missing skills were identified."
        );
        renderList(
            weakAreasList,
            data.weak_areas,
            "No weak areas were identified."
        );
        renderList(
            suggestionsList,
            data.suggestions,
            "No suggestions were generated."
        );

        rawResponse.textContent = data.raw_response || "No raw response available.";
        statusMessage.textContent = "Analysis completed successfully.";
    } catch (error) {
        console.error("Error while analyzing:", error);
        statusMessage.textContent = error.message;

        renderList(missingSkillsList, [], "Unable to load missing skills.");
        renderList(weakAreasList, [], "Unable to load weak areas.");
        renderList(suggestionsList, [], "Unable to load suggestions.");
        rawResponse.textContent = "The agent response could not be generated.";
    } finally {
        analyzeButton.disabled = false;
    }
}


analyzeButton.addEventListener("click", analyzeResume);
