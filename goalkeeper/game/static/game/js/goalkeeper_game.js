$(document).ready(function() {
    var create_seq_manually = $('#id_create_seq_manually');
    var seq_step_det_or_prob = $('#id_seq_step_det_or_prob');
    var depth = $('#id_depth');
    var sequence = $('#id_sequence');
    var operation = $('#id_operation');


    // temp solution
    if(localStorage['sequence']){
        //console.log('sequence', localStorage['sequence']);
        sequence.attr('value', JSON.parse(localStorage['sequence']));
    }

    sequence.keyup(function(){
        var currentVal = $(this).val();
        localStorage.setItem('sequence', JSON.stringify(currentVal));
    });

    // create_seq_manually.each(function() {
    //     if($(this).val() == 'yes'){
    //         console.log('y');
    //         //sequence.removeAttr('disabled');
    //         seq_step_det_or_prob.closest( ".form-group" ).hide();
    //         depth.closest( ".form-group" ).hide();
    //     } else{
    //         console.log('Nao');
    //         //sequence.attr('disabled', 'disabled');
    //         seq_step_det_or_prob.closest( ".form-group" ).show();
    //         depth.closest( ".form-group" ).show();
    //     }
    // });


    function sequenceControl(){
        //console.log('executando sequenceControl()');
       if($('#id_create_seq_manually').val() == 'yes'){
           console.log($('#id_create_seq_manually').val());
           sequence.removeAttr('disabled');
           //seq_step_det_or_prob.closest( ".form-group" ).hide();
           //depth.closest( ".form-group" ).hide();
       } else {
           console.log('setando sequencia atomatica');
           sequence.attr('disabled', 'disabled');
           //seq_step_det_or_prob.closest( ".form-group" ).show();
           //depth.closest( ".form-group" ).show();
       }
    }

    create_seq_manually.change(function(){
        sequenceControl();
    });

   sequenceControl();

    // create_seq_manually.on('change', (function () {
    //    if($(this).val() == 'yes'){
    //        sequence.prop('disabled', false);
    //        seq_step_det_or_prob.closest( ".form-group" ).hide();
    //        depth.closest( ".form-group" ).hide();
    //    } else {
    //        console.log('setando sequencia atomatica');
    //        sequence.attr('disabled', 'disabled');
    //        seq_step_det_or_prob.closest( ".form-group" ).show();
    //        depth.closest( ".form-group" ).show();
    //    }
    // }));

    // if(operation.val() == "viewing") {
    //     sequence.prop('disabled', true);
    // }
});