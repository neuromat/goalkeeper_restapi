$(document).ready(function() {
    var create_seq_manually = $('#id_create_seq_manually');
    var seq_step_det_or_prob = $('#id_seq_step_det_or_prob');
    var depth = $('#id_depth');

    create_seq_manually.each(function() {
        if($(this).val() == 'yes'){
            document.getElementById('id_sequence').readOnly = false;
            seq_step_det_or_prob.closest( ".form-group" ).hide();
            depth.closest( ".form-group" ).hide();
        } else{
            document.getElementById('id_sequence').readOnly = true;
            seq_step_det_or_prob.closest( ".form-group" ).show();
            depth.closest( ".form-group" ).show();
        }
    });

    create_seq_manually.on('change', (function () {
       if($(this).val() == 'yes'){
           document.getElementById('id_sequence').readOnly = false;
           seq_step_det_or_prob.closest( ".form-group" ).hide();
           depth.closest( ".form-group" ).hide();
       } else {
           document.getElementById('id_sequence').readOnly = true;
           seq_step_det_or_prob.closest( ".form-group" ).show();
           depth.closest( ".form-group" ).show();
       }
    }));
});