



$(document).ready(function() {
//alert(location.pathname)
//  $('.navbar-nav li').each(function() {
  let url = window.location.href;
  $('.navbar-nav li a').each(function() {
    if (this.href === url) {
      $(this).closest('li').addClass('active');
    }
  });
});
$(document).ready(function(){
$("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

})
$(document).ready(function() {
  $("#add_expense_form").on('submit',(function(e) {
      e.preventDefault();
      console.log('fff');
      var formData = new FormData(this);
      console.log(formData);
       $.ajax({
         url: "/employee/expense/save",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data)
           {
           console.log(data);
           if (data.status_is == 'Success'){
               var infoModal = $('#ignismyModal');
               infoModal.modal('show');
           }
           else{
           var infoModal = $('#ignismyModalerror');
               infoModal.modal('show');
           }
         },

      });
}));
});

$(document).ready(function() {
  $("#timesheet-form").on('submit',(function(e) {
      e.preventDefault();
      console.log('fff');
      var formData = new FormData(this);
      console.log(formData);
       $.ajax({
         url: "/employee/timesheet/save",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data)
           {
           console.log(data);
           if (data.status_is == 'Success'){
               var infoModal = $('#ignismyModal');
               infoModal.modal('show');
           }
           else{
           var infoModal = $('#ignismyModalerror');
               infoModal.modal('show');
           }
         },

      });
}));
});

$(document).ready(function() {
  $("#employee_profile_update").on('submit',(function(e) {
      e.preventDefault();
      console.log('fff');
      var formData = new FormData(this);
      formData.append('test','1');
      console.log(formData);
       $.ajax({
         url: "/employee/profile/update",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data)
           {
           console.log(data.status_is);
           if (data.status_is == 'Success'){
               var infoModal = $('#ignismyModal');
               infoModal.modal('show');
           }
           else{
           var infoModal = $('#ignismyModalerror');
               infoModal.modal('show');
           }
         },

      });
}));
});


$(document).ready(function() {
  $("#leave_request-form").on('submit',(function(e) {
      e.preventDefault();
      console.log('fff');
      var formData = new FormData(this);
      console.log(formData);
       $.ajax({
         url: "/employee/leave/request/save",
         type: "POST",
         dataType: "json",
         data: formData,
         contentType: false,
         processData:false,
         success: function(data)
           {
           console.log(data.error_message);
           if (data.status_is == 'Success'){
              var infoModal = $('#alert_msg');
                      $('#alert_msg').html('<div class="alert alert-success"><strong>Success!</strong> Leave applied successfully.</div>');
                      infoModal.css("display", "");
           setTimeout(function() { infoModal.css("display", "none");
           location.reload();}, 2000);
           }
           else{
           var infoModal = $('#alert_msg');

                      $('#alert_msg').html('<div class="alert alert-danger"><strong>Error! </strong>'+ data.error_message +'</div>');
                      infoModal.css("display", "");
           setTimeout(function() { infoModal.css("display", "none");}, 2000);




           }
         },

      });
}));
});






$(document).ready(function() {
$("ul li").on("click", function() {
    $("li").removeClass("active");
    $(this).addClass("active");
  });
});

function onchange_project(){
                project_id = document.getElementById('project').value
                var formData = new FormData();
                formData.append('project_id',project_id)
//                alert(project_id)
                $.ajax({
                url: "/project/change",
                type: "POST",
                dataType: "json",
                data: formData,
                contentType: false,
                processData:false,
                success: function(data){
                $("#task").empty();
                for(j=0; j< data.tasks.length; j++){
                $("#task").append(" <option value="+data.tasks[j].id+">" + data.tasks[j].name +
                "</option>");
                }
                }
                });
                }