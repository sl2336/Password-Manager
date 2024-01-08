//Display modal on click

const modelWrapper = document.querySelector(".modals-wrapper")

function displayModal(id){
    //close all existing modals
    const existingModal = document.querySelectorAll(".modal");
    existingModal.forEach((modal) => {
        modal.style.display = "none";
    });
    //to open the modal
    const modal = document.getElementById(id);
    modelWrapper.style.display = "flex";
    modal.style.display = "flex";
    //to close the modal
    const close = document.getElementById("close-modal")
    close.addEventListener("click", () => {
        modelWrapper.style.display = "none";
        modal.style.display = "none";
    })
}

//copy to clipboard funcitonality

function CopyToClipboard(id){
    //Selects the text element that we need to copy
    elementToCopy = document.getElementById(id);
    //selects the text in the input element (like highlighting text to copy)
    elementToCopy.select();
    //copy the highlighted text
    navigator.clipboard.writeText(elementToCopy.value).then(() => {
        //alert link has been copied
        alert("Sucessfully Copied!");
    });
    //P.S i wrote like this cause the alert was happening before the copy
    //so i wrote it as a promise (only after copying, then display alert)
}