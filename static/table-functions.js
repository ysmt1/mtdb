// Filter gyms on input to searchbox on homepage
$(document).ready(function () {
    $("#filter-row").keyup(function () {
        var value = this.value.toLowerCase().trim();

        $("#indexTable tr").each(function (index) {
            if (!index) return;
            $(this).find("td.searchable").each(function () {
                var id = $(this).text().toLowerCase().trim();
                var not_found = (id.indexOf(value) == -1);
                $(this).closest('tr').toggle(!not_found);
                return not_found;
            });
        });
        reapplyStripes()
    });
});

/* Hide rows that contain "No Ratings" in Average Rating Column,
when "All Gyms" toggle is checked*/
$(document).ready(function () {
    var tableRows

    $('#customSwitch1').change(function () {
        if (!this.checked) {
            tableRows = $('#indexTable tr:contains("No Ratings")').detach();
            reapplyStripes()
        } else {
            $(tableRows).appendTo('#indexTable');
            sortDefault();
            tableRows = null;
        }
    });
    $('#customSwitch1').change();
});

// Reapply zebra striping after calling table modification functions
function reapplyStripes() {
    $("#indexTable tr:visible").each(function (index) {
        $(this).css("background-color", !!(index & 1) ? "rgba(0,0,0,0)" : "rgba(0,0,0,0.05)");
    });
}

/*Sort table on homepage when column headers
are clicked, and alternate sortup/sortdown icon*/
function sortTable(n, object) {
    var table, vartype, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

    var object_id = object.id;
    var object_header = document.getElementById(object_id);
    var object_span = object_header.getElementsByTagName('span')[0].innerHTML;
    var presort = '<i class="fas fa-sort"></i>';
    var sortup = '<i class="fas fa-sort-up"></i>';
    var sortdown = '<i class="fas fa-sort-down"></i>';

    table = document.getElementById("indexTable");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            rowText1 = x.textContent;
            rowText2 = y.textContent;

            if (x.textContent === 'No Ratings') {
                rowText1 = '0';
            }
            if (y.textContent === 'No Ratings') {
                rowText2 = '0';
            }
            if (isNaN(rowText1) == false) {
                vartype = "number";
            }
            else {
                vartype = "string";
            }
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (vartype == "string") {
                if (dir == "asc") {
                    if (rowText1.toLowerCase() > rowText2.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
                else if (dir == "desc") {
                    if (rowText1.toLowerCase() < rowText2.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            else if (vartype == "number") {
                if (dir == "asc") {
                    if (Number(rowText1) > Number(rowText2)) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
                else if (dir == "desc") {
                    if (Number(rowText1) < Number(rowText2)) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);

            document.getElementById(object.id).getElementsByTagName('span')[0].innerHTML = sortup;

            if (dir == "desc") {
                document.getElementById(object.id).getElementsByTagName('span')[0].innerHTML = sortdown;
            }
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
    reapplyStripes()
}

// Function to sort only first column of index table
function sortDefault() {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("indexTable");
    switching = true;
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[0];
            y = rows[i + 1].getElementsByTagName("TD")[0];
            // Check if the two rows should switch place:
            if (x.textContent.toLowerCase() > y.textContent.toLowerCase()) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
    reapplyStripes()
}