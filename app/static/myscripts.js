

// disable text selection
document.onselectstart = function() {
    return false;
}

function RowClick(currenttr, lock) {
    var trs = document.getElementById('setTable').tBodies[0].getElementsByTagName('tr');
    clearAll(trs);
    toggleRow(currenttr);
}

function toggleRow(row) {
    row.className = row.className == 'selected' ? '' : 'selected';
    row.getElementsByTagName('th').item(0).getElementsByTagName('input').item(0).checked = true;
    document.getElementById('submit_btn').disabled = false
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

