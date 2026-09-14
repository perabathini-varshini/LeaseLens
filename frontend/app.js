
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const analyzeButton = document.getElementById("analyzeButton");
const message = document.getElementById("message");

// Remove previous analysis results
function clearAnalysisResults() {
    const oldResults =
        document.getElementById("analysisResults");

    if (oldResults) {
        oldResults.remove();
    }
}

// File selection
fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];

    if (!file) {
        fileName.textContent = "No document selected";
        analyzeButton.disabled = true;
        message.textContent = "";
        return;
    }

    const extension = file.name
        .toLowerCase()
        .split(".")
        .pop();

    const isValidFile =
        extension === "pdf" ||
        extension === "docx";

    if (!isValidFile) {
        fileInput.value = "";
        fileName.textContent = "No document selected";
        analyzeButton.disabled = true;
        message.textContent =
            "Please select a valid PDF or DOCX file.";
        return;
    }

    fileName.textContent = file.name;
    analyzeButton.disabled = false;
    message.textContent =
        "Document selected. Ready to analyze.";
});

// Analyze lease
analyzeButton.addEventListener("click", async function () {
    const file = fileInput.files[0];

    if (!file) {
        message.textContent =
            "Please select a lease document first.";
        return;
    }

    clearAnalysisResults();

    analyzeButton.disabled = true;
    message.textContent =
        "Analyzing lease agreement... Please wait.";

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
            "/api/analyze",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Lease analysis failed."
            );
        }

        displayAnalysisResults(data);

        message.textContent =
            "Lease analysis completed successfully.";

    } catch (error) {
        console.error(
            "Lease analysis error:",
            error
        );

        clearAnalysisResults();

        message.textContent =
            "Analysis failed: " + error.message;

    } finally {
        analyzeButton.disabled = false;
    }
});

// Display analysis results
function displayAnalysisResults(data) {
    clearAnalysisResults();

    // FastAPI returns the analysis inside data.result
    const result = data.result || {};
    const summary = result.summary || {};
    const compliance = result.compliance || [];
    const relationships = result.relationships || [];

    const totalClauses =
        summary.total_clauses || 0;

    const compliant =
        summary.compliant || 0;

    const nonCompliant =
        summary.non_compliant || 0;

    const review =
        summary.review || 0;

    const resultsContainer =
        document.createElement("div");

    resultsContainer.id = "analysisResults";

    resultsContainer.innerHTML = `
        <div class="analysis-header">
            <h2>Lease Analysis Results</h2>

            <p>
                <strong>Document:</strong>
                ${escapeHtml(
                    result.filename ||
                    data.filename ||
                    "Unknown"
                )}
            </p>
        </div>

        <div class="analysis-summary">
            <div class="summary-card">
                <h3>${totalClauses}</h3>
                <p>Total Clauses</p>
            </div>

            <div class="summary-card">
                <h3>${compliant}</h3>
                <p>Compliant</p>
            </div>

            <div class="summary-card">
                <h3>${nonCompliant}</h3>
                <p>Non-Compliant</p>
            </div>

            <div class="summary-card">
                <h3>${review}</h3>
                <p>Needs Review</p>
            </div>
        </div>

        <div class="clause-results">
            <h2>Compliance Analysis</h2>

            ${
                compliance.length
                    ? compliance
                        .map(createComplianceCard)
                        .join("")
                    : `
                        <p>
                            No compliance results
                            were returned.
                        </p>
                    `
            }
        </div>

        ${
            relationships.length
                ? `
                    <div class="relationship-results">
                        <h2>Detected Relationships</h2>

                        <p>
                            ${relationships.length}
                            relationship(s) detected
                            between lease clauses.
                        </p>
                    </div>
                `
                : ""
        }
    `;

    message.parentNode.insertBefore(
        resultsContainer,
        message.nextSibling
    );
}

// Compliance card
function createComplianceCard(item) {
    const status = item.status || "REVIEW";
    const statusClass = status.toLowerCase();

    return `
        <div class="compliance-card ${statusClass}">
            <div class="compliance-card-header">
                <h3>
                    ${escapeHtml(
                        item.clause_type ||
                        "Unknown Clause"
                    )}
                </h3>

                <span class="status-badge">
                    ${escapeHtml(status)}
                </span>
            </div>

            <p>
                <strong>Section:</strong>
                ${escapeHtml(
                    item.section_title ||
                    "Not specified"
                )}
            </p>

            <p>
                <strong>Reason:</strong>
                ${escapeHtml(
                    item.reason ||
                    "No explanation provided."
                )}
            </p>
        </div>
    `;
}

// Basic HTML escaping
function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = String(value);

    return div.innerHTML;
}