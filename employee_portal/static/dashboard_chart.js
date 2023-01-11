 function codeAddress() {
 anychart.onDocumentReady(function() {
// alert("running");

    $.ajax({
         url: "/get/planning/data",
         type: "POST",
         dataType: "json",
         contentType: false,
         processData:false,
         success: function(data)
           {
          console.log(data);
          console.log(data.data_list);

                // the data
    var data = {
      header: ["Days", "Hours"],
      rows: eval(data.data_list)};
    // create the chart
var chart = anychart.bar();

// add the data
chart.data(data);
chart.title("Last 7 Days Timesheet");
chart.container('container');
chart.draw();

         },

      });
      });

        }
        window.onload = codeAddress;