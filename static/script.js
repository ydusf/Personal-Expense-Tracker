window.addEventListener("load", () => {
    const loader = document.querySelector(".loader");

    loader.classList.add("loader-hidden");

    loader.addEventListener("transitionend", () => {
        document.body.removeChild("loader");
    });
});

function AddMt3Class(card) {
    const screenWidth = window.innerWidth;
    const selectedCard = document.getElementById(card);

    if (screenWidth < 768) {
        selectedCard.classList.add('mt-3');
    } else {
        selectedCard.classList.remove('mt-3');
    }
}

function hideField(field) {
    // Get a reference to the recurrence_interval field and its help text
    var selectedField = document.getElementById(`${field}`);
    var fieldLabel = document.querySelector('label[for="' + selectedField.id + '"]');
    var fieldHelpText = selectedField.nextElementSibling;

    console.log("hideField - selectedField:", selectedField);
    console.log("hideField - fieldLabel:", fieldLabel);
    console.log("hideField - fieldHelpText:", fieldHelpText);

    // Show the field and help text
    if (selectedField) {
        selectedField.style.display = 'none';
        if (fieldLabel) {
            fieldLabel.style.display = 'none';
        }
        if (fieldHelpText) {
            fieldHelpText.style.display = 'none';
        }
    }
}

function showField(field) {
    // Get a reference to the recurrence_interval field and its help text
    var selectedField = document.getElementById(`${field}`);
    var fieldLabel = document.querySelector('label[for="' + selectedField.id + '"]');
    var fieldHelpText = selectedField.nextElementSibling;

    // Show the field and help text
    if (selectedField) {
        selectedField.style.display = 'block';
        if (fieldLabel) {
            fieldLabel.style.display = 'block';
        }
        if (fieldHelpText) {
            fieldHelpText.style.display = 'block';
        }
    }
} 

function hideProfilePic() {
    const profilePic = document.getElementById("profile-pic");
    profilePic.style.display = 'none';
}

function showProfilePic() {
    const profilePic = document.getElementById("profile-pic");
    profilePic.style.display = 'block';
}