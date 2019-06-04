function disableRemoveButton() {
    $('#removePath').prop('disabled', true);
}

function show_modal_remove_path(item_id) {
    $('#removePath').prop('disabled', false);
    var modal_remove = document.getElementById('removePath');
    modal_remove.setAttribute("value", 'remove_path-' + item_id);
    $('#modalRemovePath').modal('show');
}