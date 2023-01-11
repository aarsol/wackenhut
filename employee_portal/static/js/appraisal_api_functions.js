function save_appraisal_participation(event)
{
 console.log("This is the appraisal")
    event.preventDefault();
      var form = $("form")[0];
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/participation/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data.participation_list)
            window.location.reload()
            var participationTable = document.getElementById("participationTable");
             for (i = 0; i < data.participation_list.length; i++) {
              var r = participationTable.rows[i + 1];
              r.innerHTML =
          "<td>" +
          data.participation_list[i]["name"] +
            "</td>" +
              "<td>" +
          data.participation_list[i]["country_id"] +
            "</td>" +
              "<td>" +
          data.participation_list[i]["start_date"] +
            "</td>" +
          "<td>" +
          data.participation_list[i]["end_date"] +
          "</td>" +
          "<td>" +
          data.participation_list[i]["duration"] +
             "</td>" +
          '<td style="text-align: center;"> <button style="font-size: 16px;background-color: #d9534f;color: white;border-color: red;width:40px !important;min-width:40px"" type="button" onclick = delete_resume_Additional_academic(' +
          data.participation_list[i]["id"] +
          ')><i class="fa fa-trash"/></button></td>';
             }
            }
          });
}



function save_committee_membership(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("committee_membership")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/committee_membership/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function save_description_data(event)
{
    event.preventDefault();
      var form = document.getElementById("description_data")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/description_data/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function initiate_appraisal_form(event)
{
    event.preventDefault();
      var form = document.getElementById("initiate_appraisal_form")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/initiate",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}



function initiate_appraisal_form_faculty(event)
{
    event.preventDefault();
      var form = document.getElementById("initiate_appraisal_form_faculty")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/initiate/faculty",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function save_section_answers(event)
{
      var data = []
      var dict = {}
      event.preventDefault();
      var form = document.getElementById("section_questions")
      console.log("This is the form",form)
      var formData = new FormData();
      for (var i = 0; i < form.length; i++){
      console.log("THis is the form element",form[i])
       if(form[i].name==="section")
        {
          var temp = {
          'section_id':form[i].value,
          'id' : form[i+1].value,
          'marks' : form[i+2].value
          }
          data.push(temp)
        }
      }
      for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          section_id_name = "section_id"+count;
          id_name = "id"+count;
          marks_name = "marks"+count;
          formData.append(section_id_name,data[i].section_id)
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
      }
      formData.append('length',data.length)
      formData.append('reporting_observations',document.getElementById("reporting_observations").value)
      formData.append('counter_sign_authority',document.getElementById("counter_sign_authority").value)
      formData.append('employee_id',document.getElementById("employee_id").value)

      formData.append('appraisal_id',document.getElementById("appraisal_id").value)

      console.log("This is a great thing",data)


          $.ajax({
            url: "/appraisal/section_questions/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function save_counter_sign_data(event)
{
      var data = []
      var dict = {}
      event.preventDefault();
      var form = document.getElementById("appraisal_counter_sign")
          var formData = new FormData(form);
      formData.append('appraisal_id',document.getElementById("appraisal_id").value)
      console.log("This is the form",form)
      var formData = new FormData(form);
          $.ajax({
            url: "/appraisal/counter_sign/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function submit_to_reporting(event)
{
    if(confirm('Are you sure you want to submit , you will not be able to edit after that!'))
    {
          var data = []
          var dict = {}
          event.preventDefault();
          var form = document.getElementById("appraisal_counter_sign")
          var formData = new FormData(form);
              $.ajax({
                url: "/appraisal/submit/reporting",
                method: "POST",
                dataType: "json",
                data: formData,
                contentType: false,
                processData: false,
                success: function (data) {
                console.log("This is the data",data)
                if(data.error)
                {
                alert(data.error)
                }
                else
                {
                 window.location.reload()
                }
                }
              });
    }
}


function submit_to_counter(event)
{
    if(confirm('Are you sure you want to submit , you will not be able to edit after that!'))
    {
      event.preventDefault();
      var form = document.getElementById("appraisal_counter_sign")
      var formData = new FormData(form);
          $.ajax({
            url: "/appraisal/submit/counter-sign",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
    }
    else
    {

    }
}

function delete_conferences_participation(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
            var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/participation/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }
}


function delete_committee_membership(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/committee_membership/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}




//Faculty Appraisal Starts here


function save_courses_taught(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("courses_taught")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/faculty/courses_taught/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function delete_courses_taught(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/faculty/courses_taught/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}



function save_student_supervision(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("student_supervision")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/student_supervision/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function delete_student_supervision(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/student_supervision/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}




function save_research_publications(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("research_publications")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/research_publications/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function delete_research_publications(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/research_publications/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}



function save_funding_entrepreneurial(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("funding_and_entrepreneurial")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/funding_entrepreneurial/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function delete_funding_entrepreneurial(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/funding_entrepreneurial/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}


function save_institutional_service(event)
{
 console.log("This is the committee membership form")
    event.preventDefault();
      var form = document.getElementById("institutional_service")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/institutional_service/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function delete_institutional_service(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/institutional_service/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}


//save personal trait

function save_personal_traits(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("personal_trait")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/personal_traits/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_personal_traits(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/personal_traits/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_personal_trait(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("personal_traits")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/personal_traits_marks/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}



//save teaching

function save_teaching(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("teaching")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/teaching/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_teaching(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/teaching/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_teaching(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("personal_traits")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/teaching/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}


//save student supervision

function save_aar_student_supervision(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("aar_student_supervision")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/aar_student_supervision/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_aar_student_supervision(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/aar_student_supervision/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_aar_student_supervision(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("personal_traits")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/aar_student_supervision/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}



//save aar research publications

function save_aar_research_publications(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("aar_research_publications")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/aar_research_publications/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_aar_research_publications(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/aar_research_publications/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_aar_research_publications(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("personal_traits")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/aar_research_publications/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}




//save aar research publications

function save_aar_funding_entrepreneurial(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("aar_funding_entrepreneurial")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/aar_funding_entrepreneurial/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_aar_funding_entrepreneurial(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/aar_funding_entrepreneurial/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_aar_funding_entrepreneurial(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("personal_traits")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/aar_funding_entrepreneurial/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}




//save aar research publications

function save_aar_institutional_services(event)
{
 console.log("This is the personal trait form")
    event.preventDefault();
      var form = document.getElementById("aar_institutional_services")
    var formData = new FormData(form);
    $.ajax({
            url: "/appraisal/aar_institutional_services/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function delete_aar_institutional_services(id)
{
      if(confirm('Are you sure you want to delete this record!'))
      {
      var formData = new FormData();
      formData.append("id",id);
          $.ajax({
            url: "/appraisal/aar_institutional_services/delete",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function update_aar_institutional_services(event)
{
      event.preventDefault()
      data=[]
      if(confirm('Are you sure you want to update this record!'))
      {
       var form = document.getElementById("aar_institutional_services")


           for (var i = 0; i < form.length; i++){

       if(form[i].name==="id")
        {
          var temp = {
          'id' : form[i].value,
//          'name':form[i+1].value,
//          'weightage':form[i+2].value,
          'marks':form[i+3].value,
          'marks_obtained' : form[i+4].value
          }
          data.push(temp)
        }
      }

    var formData = new FormData();
       for(var i=0;i<data.length;i++)
      {
          var count = i+1;
          id_name = "id"+count;
          marks_name = "marks"+count;
          marks_obtained_name = "marks_obtained"+count;
          formData.append(id_name,data[i].id)
          formData.append(marks_name,data[i].marks)
          formData.append(marks_obtained_name,data[i].marks_obtained)
      }
      console.log("THis is the form data",data)
        formData.append('length',data.length)

          $.ajax({
            url: "/appraisal/aar_institutional_services/update",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
      }
      else
      {

      }

}

function save_signing_officer_recommendations(event)
{
      var data = []
      var dict = {}
      event.preventDefault();
      var form = document.getElementById("signing_officer_recommendations_form")
      console.log("This is the form",form)
      var formData = new FormData(form);


          $.ajax({
            url: "/appraisal/signing_officer_recommendations/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (formData) {
            console.log("This is the data",formData)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}


function save_counter_sign_recommendations(event)
{
      event.preventDefault();
      var form = document.getElementById("counter_sign_recommendations_form")
      console.log("This is the form",form)
      var formData = new FormData(form);


          $.ajax({
            url: "/appraisal/counter_sign_recommendations/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",formData)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function save_senior_counter_sign_recommendations(event)
{
      event.preventDefault();
      var form = document.getElementById("senior_counter_sign_recommendations_form")
      console.log("This is the form",form)
      var formData = new FormData(form);


          $.ajax({
            url: "/appraisal/senior_counter_sign_recommendations/save",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",formData)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
}

function faculty_submit_to_reporting(event)
{
    if(confirm('Are you sure you want to submit , you will not be able to edit after that!'))
    {
          var data = []
          var dict = {}
          event.preventDefault();
          var form = document.getElementById("submit_to_reporting_faculty")
          var formData = new FormData(form);
              $.ajax({
                url: "/appraisal/faculty/submit/reporting",
                method: "POST",
                dataType: "json",
                data: formData,
                contentType: false,
                processData: false,
                success: function (data) {
                console.log("This is the data",data)
                if(data.error)
                {
                alert(data.error)
                }
                else
                {
                 window.location.reload()
                }
                }
              });
    }
}


function faculty_submit_to_counter(event)
{
    if(confirm('Are you sure you want to submit , you will not be able to edit after that!'))
    {
      event.preventDefault();
      var form = document.getElementById("faculty_submit_to_counter")
      var formData = new FormData(form);
          $.ajax({
            url: "/appraisal/faculty/submit/counter-sign",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
    }
    else
    {

    }
}

function faculty_submit_to_senior_counter(event)
{
    if(confirm('Are you sure you want to submit , you will not be able to edit after that!'))
    {
      event.preventDefault();
      var form = document.getElementById("faculty_submit_to_counter")
      var formData = new FormData(form);
          $.ajax({
            url: "/appraisal/faculty/submit/senior-counter-sign",
            method: "POST",
            dataType: "json",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
            console.log("This is the data",data)
            if(data.error)
            {
            alert(data.error)
            }
            else
            {
             window.location.reload()
            }
            }
          });
    }
    else
    {

    }
}






