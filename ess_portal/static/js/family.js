$(document).ready(function () {
$('#resume_experience').hide();
$('#resume_education').hide();
$('#resume_training').hide();
$('#resume_publication').hide();

$("#form_family_member").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/family/submit",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Adding family member',
                text: 'Please wait.',
                position: 'top-right',
                loaderBg: '#ff6849',
                icon: 'info',
                hideAfter: 1500,
                stack: 6
            });
        },
        contentType: false,
        processData:false,
        success: function(data) {
            location.reload();
        },
        error: function(){
        }
    });
}));

$("#form_resume_record").on('submit',(function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    $.ajax({
        url: "/employee/resume/add",
        type: "POST",
        dataType: "json",
        data: formData,
        beforeSend:  function () {
            $.toast({
                heading: 'Adding Resume Record',
                text: 'Please wait.',
                position: 'top-right',
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
                    hideAfter: 1500,
                    stack: 6
                });
                setTimeout(function(){location.reload()}, 2000);
            }
        },
        error: function() {
        }
    });
}));

$('#resume_type').on('change', function () {
    if ($('#resume_type :selected').attr('type') == 'Experience') {
        $('#resume_experience').show();
        $('#resume_education').hide();
        $('#resume_training').hide();
        $('#resume_publication').hide();
    }
    else if($('#resume_type :selected').attr('type') == 'Education') {
        $('#resume_experience').hide();
        $('#resume_education').show();
        $('#resume_training').hide();
        $('#resume_publication').hide();
    }
    else if($('#resume_type :selected').attr('type') == 'Training') {
        $('#resume_experience').hide();
        $('#resume_education').hide();
        $('#resume_training').show();
        $('#resume_publication').hide();
    }
    else if($('#resume_type :selected').attr('type') == 'Publications') {
        $('#resume_experience').hide();
        $('#resume_education').hide();
        $('#resume_training').hide();
        $('#resume_publication').show();
    }
});


});

