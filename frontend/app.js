const fileInput =
    document.getElementById("fileInput");

const fileName =
    document.getElementById("fileName");

const analyzeButton =
    document.getElementById("analyzeButton");

const message =
    document.getElementById("message");


fileInput.addEventListener("change", function () {

    const file = fileInput.files[0];


    if (!file) {

        fileName.textContent =
            "No document selected";

        analyzeButton.disabled = true;

        return;
    }


    fileName.textContent =
        file.name;


    analyzeButton.disabled = false;


    message.textContent =
        "Document selected.";
});


analyzeButton.addEventListener("click", function () {

    message.textContent =
        "Analysis engine will be connected in Phase 2.";

});