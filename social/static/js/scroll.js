


function scroll(username, pies, data){

d3v3.csv("../../../static/"+username+"/"+pies+"/words.csv", function(data) {
    // set the dimensions and margins of the graph

data.forEach(function(d) {

        d.count = parseInt(d.count);
    });
var margin =  {top: 20, right:-90, bottom: 20, left: 40};
var marginOverview = {top: 30, right: 150, bottom: 20, left: 40};
var selectorHeight = 40;
    var width = 900 - margin.left - margin.right;
var height = 400 - margin.top - margin.bottom - selectorHeight;
var heightOverview = 80 - marginOverview.top - marginOverview.bottom;

var maxLength = d3v3.max(data.map(function(d){ return d.word.length}))
var barWidth = maxLength * 7;
var numBars = Math.round(width/barWidth);
var isScrollDisplayed = barWidth * data.length > width;

var xscale = d3v3.scale.ordinal()
                .domain(data.slice(0,numBars).map(function (d) { return d.word; }))
                .rangeBands([0, width], .2);

var yscale = d3v3.scale.linear()
							.domain([0, d3v3.max(data, function (d) { return d.count; })])
              .range([height, 0]);


var xAxis  = d3v3.svg.axis().scale(xscale).orient("bottom");
var yAxis  = d3v3.svg.axis().scale(yscale).orient("left");
var svg = d3v3.select("#words").append("svg")
        .attr('viewBox', '0 0 ' + 950 + ' ' + 400)
//      .style('width', '100%')
//      .style('height', 'auto')
//						.attr("width", width + margin.left + margin.right)
//            .attr("height", height + margin.top + margin.bottom + selectorHeight);

var diagram = svg.append("g")
								 .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

diagram.append("g")
  		 .attr("class", "x axis")
       .attr("transform", "translate(0, " + height + ")")
       .call(xAxis);

diagram.append("g")
       .attr("class", "y axis")
       .call(yAxis);

var bars = diagram.append("g");
bars.selectAll("rect")
            .data(data.slice(0, numBars), function (d) {return d.word; })
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function (d) { return xscale(d.word); })
            .attr("y", function (d) { return yscale(d.count); })
            .attr("width", xscale.rangeBand())
            .attr("height", function (d) { return height - yscale(d.count); });


if (isScrollDisplayed)
{
  var xOverview = d3v3.scale.ordinal()
                  .domain(data.map(function (d) { return d.word; }))
                  .rangeBands([0, width], .2);
  yOverview = d3v3.scale.linear().range([heightOverview, 0]);
  yOverview.domain(yscale.domain());

  var subBars = diagram.selectAll('.subBar')
      .data(data)

  subBars.enter().append("rect")
      .classed('subBar', true)
      .attr({
          height: function(d) {
              return heightOverview - yOverview(d.count);
          },
          width: function(d) {
              return xOverview.rangeBand()
          },
          x: function(d) {

              return xOverview(d.word);
          },
          y: function(d) {
              return height + heightOverview + yOverview(d.count)
          }
      })


  var displayed = d3v3.scale.quantize()
              .domain([0, width])
              .range(d3v3.range(data.length));

  diagram.append("rect")
              .attr("transform", "translate(0, " + (height + margin.bottom) + ")")
              .attr("class", "mover")
              .attr("x", 0)
              .attr("y", 0)
              .attr("height", selectorHeight)
              .attr("width", Math.round(parseFloat(numBars * width)/data.length))
              .attr("pointer-events", "all")
              .attr("cursor", "ew-resize")
              .call(d3v3.behavior.drag().on("drag", display));
};
function display () {
    var x = parseInt(d3v3.select(this).attr("x")),
        nx = x + d3v3.event.dx,
        w = parseInt(d3v3.select(this).attr("width")),
        f, nf, new_data, rects;

//        console.log(width)


    if ( nx < 0 || nx + w > width ) return;

    d3v3.select(this).attr("x", nx);

    f = displayed(x);
    nf = displayed(nx);

    if ( f === nf ) return;

    new_data = data.slice(nf, nf + numBars);

    xscale.domain(new_data.map(function (d) { return d.word; }));
    diagram.select(".x.axis").call(xAxis);

    rects = bars.selectAll("rect")
      .data(new_data, function (d) {return d.word; });

	 	rects.attr("x", function (d) { return xscale(d.word); });

// 	  rects.attr("transform", function(d) { return "translate(" + xscale(d.word) + ",0)"; })

    rects.enter().append("rect")
      .attr("class", "bar")
      .attr("x", function (d) { return xscale(d.word); })
      .attr("y", function (d) { return yscale(d.count); })
      .attr("width", xscale.rangeBand())
      .attr("height", function (d) { return height - yscale(d.count); });

    rects.exit().remove();
}
})};




