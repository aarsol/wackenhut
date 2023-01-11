$(document).ready(function () {

$('#halfday_div').hide();
$('#halfday_shift_div').hide();

$("#form_leave_request").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/leave/request/submit",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Request Initiating',
                text: 'Please wait.',
                position: 'top-center',
                loaderBg: '#ff6849',
                icon: 'info',
                hideAfter: 1500,
                stack: 6
            });
        },
        contentType: false,
        processData:false,
        success: function(data) {
            if(data.status == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
            }
            if(data.status != 'failed') {
                $.toast({
                    heading: 'Submitted',
                    text: data.message,
                    position: 'top-left',
                    loaderBg: '#ff6849',
                    icon: 'success',
                    hideAfter: 3000,
                    stack: 6
                });
                setTimeout(function(){location.reload()}, 2000);
            }
         },
         error: function(){
         }
    });
}));

$('#leave_type').on('change', function () {
    if ($('#leave_type :selected').attr('type') == 'Casual') {
        $('#halfday_div').show();
    }
    else {
        $('#halfday_div').hide();
        if ($('#half_leave').prop('checked') == true) {
            $('#half_leave').prop('checked',false);
            $('#date_from_label').text('Date From');
            $('#date_to_div').show();
            $('#date_to').attr('required', '1');
            $('#halfday_shift_div').hide();
            $('#halfday_shift').removeAttr('required');
            $('#upload_documents').attr('required', '1');
        }
    }
})

$('#half_leave').on('change', function () {
    if ($('#half_leave').prop('checked') == true) {
        $('#date_from_label').text('Date');
        $('#date_to_div').hide();
        $('#date_to').removeAttr('required');
        $('#upload_documents').removeAttr('required');
        $('#halfday_shift_div').show();
        $('#halfday_shift').attr('required', '1');
        $('#halfday_shift').attr('required', '1');
    }
    else {
        $('#date_from_label').text('Date From');
        $('#date_to_div').show();
        $('#date_to').attr('required', '1');
        $('#halfday_shift_div').hide();
        $('#halfday_shift').removeAttr('required');
        $('#upload_documents').attr('required', '1');
    }
})

});


