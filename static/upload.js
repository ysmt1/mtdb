var input = document.querySelector('#upload-image');
var preview = document.querySelector('.preview');
var error = document.querySelector('#errors')

input.style.opacity = 0; input.addEventListener('change', updateImageDisplay); function updateImageDisplay() {
    while (preview.firstChild) {
        preview.removeChild(preview.firstChild);
        $('#errors').empty();
    }
    var curFiles = input.files;
    if (curFiles.length === 0) {
        // If no files are chosen, do the following (currently will not do anything)
        // var para = document.createElement('p');
        // para.style.border = 'none'
        // para.textContent = 'No files currently selected for upload';
        // preview.appendChild(para);
    } else {
        var list = document.createElement('ol');
        if (curFiles.length > 4) {
            list.style.textAlign = 'center'
        }
        preview.appendChild(list);
        for (var i = 0; i < curFiles.length; i++) {
            var listItem = document.createElement('li');
            listItem.className = "img-list"
            var para = document.createElement('p');
            if (validFileType(curFiles[i])) {
                // Code below will give file description with image.  Currently just want image
                //para.textContent = 'File name ' + curFiles[i].name + ', file size ' + returnFileSize(curFiles[i].size) + '.';
                var image = document.createElement('img');
                image.src = window.URL.createObjectURL(curFiles[i]);

                listItem.appendChild(image);
                //listItem.appendChild(para);
                list.appendChild(listItem);
                
                if (curFiles[i].size > 3145728) {
                    var errorDiv = document.createElement('div')
                    errorDiv.className = "alert alert-warning error-div"
                    errorDiv.textContent = `File ${curFiles[i].name} is too large (${returnFileSize(curFiles[i].size)}).  Clear files and update your selection.`;
                    error.appendChild(errorDiv);
                }
            } else {
                var errorDiv = document.createElement('div')
                errorDiv.className = "alert alert-danger error-div"
                errorDiv.textContent = 'File name ' + curFiles[i].name + ': Not a valid file type. Update your selection.';
                error.appendChild(errorDiv);
            }
        }
    } 
} 

// Empty file list when button is clicked
$('#clear-files').click(function() {
    $('.img-list').remove();
    $('#upload-image').val('');
    $('#errors').empty();
})

var fileTypes = [
    'image/jpeg',
    'image/pjpeg',
    'image/png'
]

// Check if files chosen are of valid types
function validFileType(file) {
    for (var i = 0; i < fileTypes.length; i++) {
        if (file.type === fileTypes[i]) {
            return true;
        }
    }
    return false;
} 

// Return file size in bytes
function returnFileSize(number) {
    if (number < 1024) {
        return number + 'bytes';
    } else if (number >= 1024 && number < 1048576) {
        return (number / 1024).toFixed(1) + 'KB';
    } else if (number >= 1048576) {
        return (number / 1048576).toFixed(1) + 'MB';
    }
}