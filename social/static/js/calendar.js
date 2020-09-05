
function drawCalendar(username, pies, myData) {
d3.csv("../../../../static/"+username+"/"+pies+"/calendar.csv", function(myData) {

  var calendarRows = function(month) {
    var m = d3.timeMonth.floor(month);
    return d3.timeWeeks(d3.timeWeek.floor(m), d3.timeMonth.offset(m,1)).length;
  }

  var minDate = d3.min(myData, function(d) { return new Date(d.day); });
  var maxDate = d3.max(myData, function(d) { return new Date(d.day); });

  var cellMargin = 2,
      cellSize = 20;

  var day = d3.timeFormat("%w"),
      week = d3.timeFormat("%U"),
      format = d3.timeFormat("%Y-%m-%d"),
      titleFormat = d3.utcFormat("%a, %d-%b"),
      monthName = d3.timeFormat("%B"),
      months= d3.timeMonth.range(d3.timeMonth.floor(minDate), maxDate);

  for(var i=0; i<myData.length; i++){
    myData[i].today =  myData[i].day.slice(0,10);
  }

  var svg = d3.select("#calendar").selectAll("svg")
    .data(months)
    .enter().append("svg")
      .attr("class", "month")
      .attr("width", (cellSize * 7) + (cellMargin * 8) )
      .attr("height", function(d) {
        var rows = calendarRows(d);
        return (cellSize * rows) + (cellMargin * (rows + 1)) + 20; // the 20 is for the month labels
      })
    .append("g")

  svg.append("text")
    .attr("class", "month-name")
    .attr("x", ((cellSize * 7) + (cellMargin * 8)) / 2 )
    .attr("y", 15)
    .attr("text-anchor", "middle")
    .text(function(d) { return monthName(d); })

  var rect = svg.selectAll("rect.day")
    .data(function(d, i) {
      return d3.timeDays(d, new Date(d.getFullYear(), d.getMonth()+1, 1));
    })
    .enter().append("rect")
      .attr("class", "day")
      .attr("width", cellSize)
      .attr("height", cellSize)
      .attr("rx", 3).attr("ry", 3) // rounded corners
      .attr("fill", '#eaeaea') // default light grey fill
      .attr("x", function(d) {
        return (day(d) * cellSize) + (day(d) * cellMargin) + cellMargin;
      })
      .attr("y", function(d) {
        return ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellSize) +
               ((week(d) - week(new Date(d.getFullYear(),d.getMonth(),1))) * cellMargin) +
               cellMargin + 20;
       })
      .on("mouseover", function(d) {
        d3.select(this).classed('hover', true);
      })
      .on("mouseout", function(d) {
        d3.select(this).classed('hover', false);
      })
      .datum(format);

  rect.append("title")
    .text(function(d) { return titleFormat(new Date(d)); });

  var lookup = d3.nest()
    .key(function(d) { return d.today; })
    .rollup(function(leaves) { return leaves.length; })
    .object(myData);

  var lookup1 = d3.nest()
  .key(function(d) { return d.today; })
    .object(myData);

  count = d3.nest()
    .key(function(d) { return d.today; })
    .rollup(function(leaves) { return leaves.length; })
    .entries(myData);

  scale = d3.scaleLinear()
    .domain(d3.extent(count, function(d) { return parseInt(d.value); }))
    .range([0.4,1]); // the interpolate used for color expects a number in the range [0,1] but i don't want the lightest part of the color scheme

rect.filter(function(d) { return d in lookup1; })
    .style("fill", function(d) { return d3.interpolatePuBu(scale(lookup[d])); })
    .classed("clickable", true)
    .on("click", function(d){
      if(d3.select(this).classed('focus')){
        d3.select(this).classed('focus', false);
      } else {
        d3.select(this).classed('focus', true)
      }

      string = JSON.stringify(lookup1[d][0].link);
      console.log(lookup[d]);
      console.log(string)
      clean = string.replace(/"([^"]+(?="))"/g, '$1');
      window.open(clean, '_blank');
    })
    .select("title")
      .text(function(d) { return titleFormat(new Date(d)) + ":  " + lookup[d]; });
}
)

}
;
