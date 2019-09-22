/*Convert numbers to display star icons on gym review pages*/
document.addEventListener('DOMContentLoaded', function() {

    var styleicon = document.createElement('style');
    styleicon.innerHTML = '.my-icon {text-shadow: 0 0 2px #000}';
    document.head.appendChild(styleicon);

    var ratingnum = document.querySelectorAll('span.rating');
    var starcode = '<span style="font-size: 1em; color: Gold;"><i class="fas fa-star my-icon"></i> </span>';
    var emptystar = '<span style="font-size: 1em; color: white;"><i class="fas fa-star my-icon"></i> </span>'

    for (var i = 0, len = ratingnum.length; i<len; i++){
        
        if (ratingnum[i].innerHTML === '5') {
            ratingnum[i].innerHTML = starcode.repeat(5);
        }
        else if (ratingnum[i].innerHTML === '4') {
            ratingnum[i].innerHTML = starcode.repeat(4) + emptystar;
        }
        else if (ratingnum[i].innerHTML === '3') {
            ratingnum[i].innerHTML = starcode.repeat(3) + emptystar.repeat(2);
        } 
        else if (ratingnum[i].innerHTML === '2') {
            ratingnum[i].innerHTML = starcode.repeat(2) + emptystar.repeat(3);
        }
        else if (ratingnum[i].innerHTML === '1') {
            ratingnum[i].innerHTML = starcode.repeat(1) + emptystar.repeat(4);
        } 
    }
})

function updateTextInput(val) {
    document.getElementById('OutputId').value = val;
}