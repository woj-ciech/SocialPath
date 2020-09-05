function lolipop(username, pies, data) {

d3.csv("../../../static/"+username+"/"+pies+"/hashtags.csv", function(data) {


counter = 0
data.forEach(function(d) {

        d.count = parseInt(d.count);
        counter = counter + 1
    });

    var maxCount = d3.max(data, function(d) {
        return d.count;
    });

    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 40, left: 100},
    width = 900 - margin.left - margin.right,
    height = 20 * counter - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var svg = d3.select("#hashtags")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    // Parse the Data

    // Add X axis
    var x = d3.scaleLinear()
        .domain([0, maxCount])
        .range([0, width]);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");

    // Y axis
    var y = d3.scaleBand()
        .range([0, height])
        .domain(data.map(function(d) {
            return d.hashtag;
        }))
        .padding(1);
    svg.append("g")
        .call(d3.axisLeft(y))


    // Lines
    svg.selectAll("myline")
        .data(data)
        .enter()
        .append("line")
        .attr("x1", function(d) {
            return x(d.count);
        })
        .attr("x2", x(0))
        .attr("y1", function(d) {
            return y(d.hashtag);
        })
        .attr("y2", function(d) {
            return y(d.hashtag);
        })
        .attr("stroke", "grey")

    // Circles
    svg.selectAll("mycircle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) {
            return x(d.count);
        })
        .attr("cy", function(d) {
            return y(d.hashtag);
        })
        .attr("r", "4")
        .style("fill", "#69b3a2")
        .attr("stroke", "black")
}

)};