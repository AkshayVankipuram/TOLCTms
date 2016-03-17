$(function () {

	var root = null,
		width = $("#chartcontainer").width(),
		height = screen.availHeight * .7,
		margin = {top: 20, left: 20, bottom: 20, right: 20},
		diameter = Math.min(width, height),
		center = [width / 2, height / 2];
		
    var svg = d3.select("#chartcontainer").append("svg")
        .attr("width", width - margin.left - margin.right)
        .attr("height", height - margin.top - margin.bottom)
        .append("g");
	
	var loadingText = svg.append("text")
		.style("text-anchor", "middle")
		.attr("x", center[0])
		.attr("y", center[1])
		.text("Loading ...");

	var selected = false;

    var group = {};

	d3.json("/chart_data/?course="+course_name, function(err, res) {

		if(err) throw err;

        root = res;
		
        update(root);

	});

	function update(node) {

		loadingText.remove();

		d3.select("#chartcontainer").select("svg").remove();

		var svg = d3.select("#chartcontainer").append("svg")
            .attr("width", width - margin.left - margin.right)
            .attr("height", height - margin.top - margin.bottom)
			.append("g");

		var nodes = classes(dataTransformSkills(node.children));
		
		var force = d3.layout.force()
			.nodes(nodes)
			.size([width, height]);

		var gnodes = svg.selectAll("g")
			.data(nodes)
			.enter().append("g");

		gnodes.append('circle')
            .attr("r",0)
            .style("fill",function(d) {
                if(d.selected) {
  				    return colorvalues.greens[5];
                } else {
  				    return colorvalues.greens[3];
                }
            })
            .style("opacity",.9)
            .style("stroke",colorvalues.greens[5])
            .style("stroke-width","1.5px")
            .on('mouseenter', function(d) {
                d3.select(this)
                    .transition()
                    .attr("r", d.r*1.1)
                    .style("fill", colorvalues.greens[5]);
            })
            .on("mouseleave", function(d) {
                if(!d.selected) {
                    d3.select(this)
                        .transition()
                        .attr("r", d.r)
                        .style("fill", colorvalues.greens[3]);
                }
            })
            .on('click', function(d) {
				var f = node.children.filter(function(n) { return n.name == d.name; });	
				if(f.length > 0 && 'children' in f[0]) {
					selected = true;
					d3.select(".inner").text(f[0].name);
					update(f[0]);
				} else {
                    if(Object.keys(group).length < 4 && !(d.name in group)) {
                        d.selected = true;
                        var n = this
                        d3.select(n)
                            .attr("r", d.r*1.1)
                            .style("fill", colorvalues.greens[5]);
                        group[d.name] = d.value;
                        $("<li>")
                            .addClass("list-group-item")
                            .addClass(d.name)
                            .html(d.name + "<code>"+node.name+"</code>")
                            .append($("<i>")
                                .addClass("fa")
                                .addClass("fa-times")
                                .css("float", "right")
                                .css("cursor", "pointer")
                                .on("click", function() {
                                    $("."+d.name).remove();
                                    d.selected = false;
                                    d3.select(n)
                                        .attr("r", d.r)
                                        .style("fill", colorvalues.greens[3]);
                                    delete group[d.name];
                                }))
                            .insertBefore(".group .footer");
                        $("#groupvar").text(getVariance());
				    }
                }
            });

        gnodes.append("text")
        	.style("text-anchor", "middle")
        	.style("font-size", "10px")
        	.style("pointer-events", "none")
        	.style("opacity", 0)
        	.text(function(d) { return d.name; });

        gnodes.selectAll('circle').transition().duration(1000).attr("r", function(d) { 
            if(d.selected) {
                return d.r * 1.1; 
            } else {
                return d.r;
            }
        });
        gnodes.selectAll('text').transition().duration(1000).style("opacity", .9);
        
        force.gravity(-0.015)
            .charge(function(d) { return -Math.pow(d.r, 2.0) / 8; })
            .friction(0.9)
            .on('tick', function(e) {
                gnodes.selectAll('circle').each(function(d) {
                    d.x = d.x + (center[0] - d.x) * (0.1 + 0.02) * e.alpha;
                    d.y = d.y + (center[1] - d.y) * (0.1 + 0.02) * e.alpha;
                })
                .attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });

                gnodes.selectAll('text')
                	.attr("x", function(d) { return d.x; })
                	.attr("y", function(d) { return d.y; });
            })
            .start();     

        setTimeout(function() { force.stop(); },10000);
	}

	d3.select("#back")
		.on("click", function() {
			if(selected) {
				d3.select(".inner").text(root.name);
				update(root);
				selected = false;
			}
		});

	function dataTransformSkills(node) {
		return [node.map(function(d) { 
			if(d.children === undefined) {
				return {
					'name': d.name,
					'size': d.size
				};
			} else {
				return {
					'name': d.name,
					'size': d.children.length
				};
			}
		}), node.length];
	}

    function getVariance() {
        var sum = 0;
        for(var k in group)
            sum += group[k];
        var avg = sum / Object.keys(group).length;
        var ss = 0;
        for(var k in group) {
            ss += Math.pow((group[k] - avg), 2);
        }
        return ss / Object.keys(group).length;
    }

	function classes(arr) {
		var nodes = arr[0];
		var c = [];
		var max = d3.max(nodes, function(d) { return d.size; });
		var radius = d3.scale.pow().exponent(0.5).domain([0,max]).range([0, (arr[1] < 50) ? 50: 40]);
		nodes.forEach(function(d) {
			c.push({ 
		        name: d.name,
		        r: radius(d.size),
		        value: d.size,
		        x: Math.random() * width,
		        y: Math.random() * height,
                selected: (d.name in group) 
		    });
		});
		c.sort(function(a,b) { return b.value - a.value; });
		return c;
	}

});
