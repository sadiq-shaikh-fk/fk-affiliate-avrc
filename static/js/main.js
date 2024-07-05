document.getElementById('browseText').addEventListener('click', function () {
    document.getElementById('fileInput').click();
});


//drag and drop upload code
var dropArea = document.getElementById('dropArea');

dropArea.addEventListener('dragover', function (event) {
    event.preventDefault();
    dropArea.classList.add('drag-over');
});

dropArea.addEventListener('dragleave', function (event) {
    event.preventDefault();
    dropArea.classList.remove('drag-over');
});

dropArea.addEventListener('drop', function (event) {
    event.preventDefault();
    dropArea.classList.remove('drag-over');
    var files = event.dataTransfer.files;
    handleFiles(files);
});

document.getElementById('fileInput').addEventListener('change', function (event) {
    var files = event.target.files;
    handleFiles(files);
});

// Declare the uploadTasks array to keep track of all upload tasks
var uploadTasks = [];

function handleFiles(files) {
    for (let i = 0; i < files.length; i++) {
        let file = files[i];
        // Create an upload task object for each file
        let uploadTask = { file: file, cancelled: false, interval: null };
        uploadTasks.push(uploadTask); // Add the upload task to the array
        let uploadingFileElement = createUploadingFileElement(file.name, uploadTask);
        document.getElementById('uploadingFiles').appendChild(uploadingFileElement);

        let loadingBar = uploadingFileElement.querySelector('.loading-bar');
        animateLoadingBar(loadingBar, file.name, uploadTask);
    }
}

function createUploadingFileElement(fileName) {
    let uploadingFileElement = document.createElement('div');
    uploadingFileElement.className = 'uploading-file';
    uploadingFileElement.innerHTML = `
    <div class="heading-uploaded">
                <b class="upload">Uploading </b>
            </div>
    <div class="grey-outline">
        <div class="document-name">
            <div class="supported-formates-jpeg">${fileName}</div>
            <img class="vector-icon" src="./assets/close.svg" onclick="cancelUpload(this)">
        </div>
    </div>
    <div class="loading-bar">
        <div></div>
    </div>
`;
    return uploadingFileElement;
}

//loading bar code
function animateLoadingBar(loadingBar, fileName, uploadTask) {
    let width = 0;
    let interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
            if (!uploadTask.cancelled) {
                setTimeout(() => {
                    let uploadedFileElement = createUploadedFileElement(fileName);
                    document.getElementById('uploadedFiles').appendChild(uploadedFileElement);

                    // Remove from uploading section after move to uploaded section
                    let uploadingFileElements = document.querySelectorAll('.uploading-file');
                    for (let element of uploadingFileElements) {
                        if (element.querySelector('.document-name .supported-formates-jpeg').textContent === fileName) {
                            element.remove();
                            break;
                        }
                    }
                }, 500); // Delay before moving to uploaded section
            }
        } else {
            width++;
            loadingBar.style.width = width + '%';
        }
    }, 20); // Adjust this value to change the speed of the loading animation
    // Store the interval on the upload task object
    uploadTask.interval = interval;
}

function createUploadedFileElement(fileName) {
    let uploadedFileElement = document.createElement('div');
    uploadedFileElement.className = 'uploaded-file';
    uploadedFileElement.innerHTML = `
    <div class="green-outline">
        <div class="document-name-1">
            <div class="supported-formates-jpeg">${fileName}</div>
            <img class="delete-img" src="./assets/delete.svg" onclick="deleteFile(this)" />
        </div>
    </div>
`;
    return uploadedFileElement;
}

//card Height adjusting code 
function adjustBackgroundHeight() {
    const whiteBackground = document.getElementById("whiteBackground");
    const uploadingFiles = document.getElementById("uploadingFiles");
    const uploadedFiles = document.getElementById("uploadedFiles");

    const totalHeight = uploadingFiles.offsetHeight + uploadedFiles.offsetHeight + 100; // 100 is padding/margin or some buffer

    whiteBackground.style.height = totalHeight + "px";
}


// Add this new function (Delete Funtion)
function deleteFile(deleteIcon) {
    let fileElement = deleteIcon.closest('.uploaded-file');
    fileElement.remove();
}

function findUploadTask(fileName) {
    return uploadTasks.find(task => task.file.name === fileName);
}

// Add this new function (Cancel uploading function)
function cancelUpload(vectorIcon) {
    let fileElement = vectorIcon.closest('.uploading-file');
    let fileName = fileElement.querySelector('.document-name .supported-formates-jpeg').textContent;
    // Find the upload task object
    let uploadTask = findUploadTask(fileName);
    if (uploadTask) {
        uploadTask.cancelled = true; // Set the cancelled flag
        clearInterval(uploadTask.interval); // Clear the upload interval
        uploadTasks = uploadTasks.filter(task => task.file.name !== fileName); // Remove the task from the array
    }
    fileElement.remove();
}
