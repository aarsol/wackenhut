$(document).ready(function () {
$("#checkin_date_div").hide();
$("#checkin_time_div").hide();
$("#checkout_date_div").hide();
$("#checkout_time_div").hide();
$('#checkout_date_div').hide();
 $('#checkout_time_div').hide();
$('#checkin').on('change', function () {
if ($('#checkin').prop('checked') == true) {
        $('#checkin_date_div').show();
        $('#checkin_time_div').show();
    }
    else {
        $('#checkin_date_div').hide();
        $('#checkin_time_div').hide();
    }
    })
$('#checkout').on('change', function () {
if ($('#checkout').prop('checked') == true) {
        $('#checkout_date_div').show();
        $('#checkout_time_div').show();
    }
    else {
         $('#checkout_date_div').hide();
        $('#checkout_time_div').hide();
    }
    })

$("#form_missed_att").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/missed/att/submit",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Request Initiated',
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
            if(data.failed == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
            }
            if(!(data.failed == 'failed')) {
                $.toast({
                    heading: 'Submitted',
                    text: data.message,
                    position: 'top-left',
                    loaderBg: '#ff6849',
                    icon: 'success',
                    hideAfter: 2000,
                    stack: 6
                });
                setTimeout(function(){location.reload()}, 2500);
            }
        },
        error: function()
        {

        }
    });
}));

$("#form_advance_payment").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/advance/payment/submit",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Request Initiated',
                text: 'Please wait.',
                position: 'top-center',
                loaderBg: '#ff6849',
                icon: 'success',
                hideAfter: 1500,
                stack: 6
            });
        },
        contentType: false,
        processData:false,
        success: function(data) {
            if(data.failed == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
            }
            if(!(data.failed == 'failed')) {
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
        error: function()
        {

        }
      });
}));

$("#form_travel_request").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/travel/request/submit",
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
            if(data.failed == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
            }
            if(!(data.failed == 'failed')) {
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
        error: function()
        {

        }
    });
}));

$("#form_resign_request").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/resign/request/submit",
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
            if(data.failed == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
            }
            if(!(data.failed == 'failed')) {
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
        error: function()
        {

        }
      });
   }));
});

function approve_request(model_name,rec_id){
    var formData = new FormData();
    formData.append('model_name',model_name)
    formData.append('rec_id',rec_id)
    $.ajax({
        url: "/employee/team/request/approve",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Approving',
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
            if(data.failed == 'failed') {
            $(".alerttop_error_message").text(data.message);
            $(".alerttop").fadeToggle(350);
        }
            if(!(data.failed == 'failed')) {
            $.toast({
                heading: 'Approved',
                text: data.message,
                position: 'top-left',
                loaderBg: '#ff6849',
                icon: 'success',
                hideAfter: 3000,
                stack: 6
            });
            var pending_card = data.pending_request_model+'_'+data.request_id;
            $('#'+pending_card).remove();
           // setTimeout(function(){location.reload()}, 2000);
        }
        },
        error: function()
        {
            showNotify('Something went wrong!','danger','top-right');
        }
   });
}

function reject_request(model_name,rec_id){
    var formData = new FormData();
    formData.append('model_name',model_name)
    formData.append('rec_id',rec_id)
    $.ajax({
        url: "/employee/team/request/reject",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Rejecting',
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
            if(data.failed == 'failed') {
                $(".alerttop_error_message").text(data.message);
                $(".alerttop").fadeToggle(350);
             }
            if(!(data.failed == 'failed')) {
                $.toast({
                    heading: 'Rejected',
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
        error: function()
        {
            showNotify('Something went wrong!','danger','top-right');
        }
    });
}

function cancel_request(model_name,rec_id){
    var formData = new FormData();
    formData.append('model_name',model_name)
    formData.append('rec_id',rec_id)
    $.ajax({
        url: "/employee/request/cancel",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Cancelling',
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
            if(data.failed == 'failed') {
            $(".alerttop_error_message").text(data.message);
            $(".alerttop").fadeToggle(350);
        }
            if(!(data.failed == 'failed')) {
            $.toast({
                heading: 'Cancelled',
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
        error: function()
        {
            showNotify('Something went wrong!','danger','top-right');
        }
   });
}