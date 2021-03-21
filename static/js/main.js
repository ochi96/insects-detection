$(document).ready(function() {
    $('.round-chart').easyPieChart({
    'scaleColor': false,
    'lineWidth': 20,
    'lineCap': 'butt',
    'barColor': '#6d5cae',
    'trackColor': '#e5e9ec',
    'size': 190
    });
    $('#performance-eval .spider-chart').highcharts({
        chart: {
        polar: true,
        type: 'area'
    },
        title: {
        text: ''
    },
        xAxis: {
        categories: ['Temperature', 'Ambient Pressure', 'Relative Humidity', 'Exhaust Vacuum'],
        tickmarkPlacement: 'on',
        lineWidth: 0
    },
        yAxis: {
        gridLineInterpolation: 'polygon',
        lineWidth: 0,
        min: 0
    },
        tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}">{series.name}:<b>{point.y:,.0f}</b><br/>'
    },
        legend: {
        align: 'right',
        verticalAlign: 'top',
        y: 70,
        layout: 'vertical'
    },
        series: [{
        name: 'Maximum',
        data: [450, 39, 58, 630],
        pointPlacement: 'on',
        color: '#676F84'
    },
    {
        name: 'Current Readings',
        data: [830, 49, 60, 350],
        pointPlacement: 'on',
        color: '#f35958'
    }]
    });


var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
} 

var slider = document.getElementById("myRange1");
var output = document.getElementById("demo1");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
} 

var slider = document.getElementById("myRange2");
var output = document.getElementById("demo2");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
} 

var slider = document.getElementById("myRange3");
var output = document.getElementById("demo3");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
} 

});
