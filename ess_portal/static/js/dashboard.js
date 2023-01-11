$( document ).ready(function() {
    "use strict";

 /*   var availed = JSON.parse($('#availed_leave').text());
    var total = JSON.parse($('#total_leave').text());
    var cat = JSON.parse($('#att_allocation_category').text());

    var options = {
          series: [{
          name: 'Availed',
          data: availed,
        }, {
          name: 'Total',
          data: total,
        }],
          chart: {
          type: 'bar',
          height: 250,
			  toolbar: {
        		show: false,
			  }
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '30%',
            borderRadius: 3
          },
        },
        dataLabels: {
          enabled: false,
        },
		grid: {
			show: false,
			padding: {
			  top: 0,
			  bottom: 0,
			  right: 30,
			  left: 20
			}
		},
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
		colors: ['rgba(255, 255, 255, 0.25)', '#f7f7f7'],
        xaxis: {
          categories: cat,
			labels: {
          		show: false,
			},
			axisBorder: {
          		show: false,
			},
			axisTicks: {
          		show: false,
			},
        },
        yaxis: {
          labels: {
          		show: false,
			}
        },
		 legend: {
      		show: false,
		 },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function (val) {
              return "" + val + " Days"
            }
          },
			marker: {
			  show: false,
		  },
        }
        };
    var chartre = document.querySelector("#leaves_chart");

var chart = new ApexCharts(chartre, options);
        chart.render();*/



// 3D pie leaves chart
debugger;
//    var leaves_allocated = JSON.parse($('#leaves_allocated').text());
    var leaves_data = JSON.parse($('#leaves_data').text());
//    var total_available = JSON.parse($('#total_available').text());
//    leaves_data.push({
//        name: 'Leaves Allocated',
//        y: leaves_allocated,
//        sliced: false,
//        selected: false,
//        color: '#FB8500',
//    });
//    leaves_data.push({
//        name: 'Total Available',
//        y: total_available,
//        sliced: true,
//        selected: true,
//        color: '#588157',
//    });
    Highcharts.chart('piechartleaves', {
        chart: {
            type: 'pie',
            options3d: {
                enabled: true,
                alpha: 45,
                beta: 0
            }
        },

        title: {
            text: 'My Leaves Summary'
        },
        credits: {
            enabled: false
        },
        /*subtitle: {
            text: 'Source: ' +
                '<a href="https://www.counterpointresearch.com/global-smartphone-share/"' +
                'target="_blank">Counterpoint Research</a>'
        },*/
        accessibility: {
            point: {
               valueSuffix: 'Available'
            }
        },
        tooltip: {
            //pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        navigation: {
            buttonOptions: {
            enabled: false
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            depth: 20,
            dataLabels: {
                enabled: false,
                format: '{point.name}',
                connectorShape: 'fixedOffset'
//                connectorShape: 'crookedLine',
//    crookDistance: '70%'
            },
            showInLegend: true
        }
    },
    series: [{
        type: 'pie',
        colorByPoint: true,
        name: 'Days',
        data: leaves_data
    }]
});

});