// window.location.reload(false); 


// disable text selection
document.onselectstart = function() {
    return false;
}

// Allow rows to be selected in radio-table
function RowClick(current_tr, lock) {
    var trs = document.getElementById('radio-table').tBodies[0].getElementsByTagName('tr');
    clearAll(trs);
    toggleRow(current_tr);
}

function toggleRow(row) {
    row.className = row.className == 'selected' ? '' : 'selected';
    row.getElementsByTagName('th').item(0).getElementsByTagName('input').item(0).checked = true;
    document.getElementById('submit_button').disabled = false
}

function clearAll(trs) {
    for (var i = 0; i < trs.length; i++) {
        trs[i].className = '';
        trs[i].getElementsByTagName('th').item(0).getElementsByTagName('input').item(0).checked = false;
    }
}


// Change image color on dropdown select
function colorChange() {
    var img_url = JSON.parse(document.getElementById("color_select").value.replace(/'/g, '"')).image;
    document.getElementById("color_image").src = img_url;
}

// Search (Filter) table entries
function searchTable() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("table_search");
    filter = input.value.toUpperCase();
    table = document.getElementById("searchable_table");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function addLoader() {
    var button = document.getElementById("loadBtn");
    // var button2 = document.getElementsByClass("BUTTON")
    var span = document.createElement("SPAN");
    span.classList.add("spinner-border", "spinner-border-sm", "ml-2")
    button.appendChild(span);
    button.disabled = true;
    // button.disabled = true;
}

function formLoader() {
    var button = document.getElementById("loadBtn");
    // var button2 = document.getElementsByClass("BUTTON")
    var span = document.createElement("SPAN");
    span.classList.add("spinner-border", "spinner-border-sm", "ml-2")
    button.appendChild(span);
    button.disabled = true;
    // button.disabled = true;
}

function formLoader2() {
    var button = document.getElementById("loadBtn2");
    // var button2 = document.getElementsByClass("BUTTON")
    var span = document.createElement("SPAN");
    span.classList.add("spinner-border", "spinner-border-sm", "ml-2")
    button.appendChild(span);
    button.disabled = true;
    // button.disabled = true;
}

// Spinner

