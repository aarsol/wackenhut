//[Dashboard Javascript]

//Project:	CRMi - Responsive Admin Template
//Primary use:   Used only for the main dashboard (index.html)


$(function () {

  'use strict';
	
		 
	var options = {
          series: [70, 38],
          chart: {
          type: 'donut',
			 height: 240,
			  width: 240,
        },
		legend: {
      		show: false,
		},
		dataLabels: {
			enabled: false,
		  },
		plotOptions: {
			pie: {
			  customScale: 0.90,
			  donut: {
				size: '80%',
				  labels: {
					show: true,
					total: {
					  showAlways: true,
					  show: true,
					}
				  }
			  },
			  offsetY: 0,
			},
			stroke: {
			  colors: undefined
			}
		  },
		colors:['#7047ee', '#e8e1ff'],
        };

        var chart = new ApexCharts(document.querySelector("#chart41"), options);
        chart.render();
	
	
	 var analyticsBarChartOptions = {
		chart: {
		  height: 210,
		  type: 'bar',
		  toolbar: {
			show: false
		  }
		},
		plotOptions: {
		  bar: {
			horizontal: false,
			columnWidth: '40%',
			borderRadius: 3
		  },
		},
		dataLabels: {
		  enabled: false
		},
		colors: ['#3596f7', '#cce5ff'],
		series: [{
		  name: 'Project',
		  data: [80, 95, 150, 210, 140, 230, 300]
		}, {
		  name: 'Bench',
		  data: [50, 70, 130, 180, 90, 180, 270]
		}],
		xaxis: {
		  categories: ['Sun', 'Mon', 'Tur', 'Wed', 'Thu', 'Fri', 'Set'],
		  axisBorder: {
			show: false
		  },
		  axisTicks: {
			show: false
		  },
		  labels: {
			style: {
			  colors: '#333333'
			}
		  }
		},
		yaxis: {
		  min: 0,
		  max: 300,
		  tickAmount: 3,
		  labels: {
			style: {
			  color: '#333333'
			}
		  }
		},
		legend: {
		  show: false, 
		},
	  }

	  var analyticsBarChart = new ApexCharts(
		document.querySelector("#analytics-bar-chart"),
		analyticsBarChartOptions
	  );

	  analyticsBarChart.render();
	
	
	
	var analyticsBarChartOptions = {
		chart: {
			height: 243,
			type: 'bar',
			toolbar: {
			show: false
		  }
		},
		plotOptions: {
		  bar: {
			horizontal: false,
			columnWidth: '45%',
			borderRadius: 3
		  },
		},
		dataLabels: {
		  enabled: false
		},
		colors: ['#7047ee'],
		series: [{
		  name: 'Turnover',
		  data: [80, 95, 150, 210, 140, 230, 300, 280, 130]
		}],
		xaxis: {
		  categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
		  axisBorder: {
			show: false
		  },
		  axisTicks: {
			show: false
		  },
		  labels: {
			style: {
			  colors: '#333333'
			}
		  }
		},
		yaxis: {
		  min: 0,
		  max: 300,
		  tickAmount: 3,
		  labels: {
			style: {
			  color: '#333333'
			}
		  }
		},
		legend: {
		  show: false, 
		},
		tooltip: {
		  y: {
			formatter: function (val) {
			  return "$ " + val + " thousands"
			}
		  }
		}
	  }

	  var analyticsBarChart = new ApexCharts(
		document.querySelector("#staff_turnover"),
		analyticsBarChartOptions
	  );

	  analyticsBarChart.render();
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
}); // End of use strict
