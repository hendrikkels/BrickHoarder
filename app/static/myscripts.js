var lastSelectedRow;
var trs = document.getElementById('tableStudent').tBodies[0].getElementsByTagName('tr');

// disable text selection
document.onselectstart = function() {
    return false;
}

function RowClick(currenttr, lock) {
    clearAll();
    toggleRow(currenttr);
}

function toggleRow(row) {
    row.className = row.className == 'selected' ? '' : 'selected';
    lastSelectedRow = row;
}

function clearAll() {
    for (var i = 0; i < trs.length; i++) {
        trs[i].className = '';
    }
}

// Change image color on dropdown select
function colorChange() {
    var img_url = document.getElementById("color_select").value;
    document.getElementById("color_image").src = img_url;
}

