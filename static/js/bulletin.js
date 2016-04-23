var table = null;
$(function () {

    var table_href = "/table_data/?course="+coursename+'&task='+taskname+'&objective='+objective;
    //var href = "/table_data/"+location.search;
	table = $("#userlist").DataTable({
		ajax: table_href,
        processing: true,
		responsive: true,
		autoWidth: false,
		lengthMenu: [ 20, 40 ],
        order: [[hidden, "desc"]],
        columnDefs: [
            {
                targets: [ hidden ],
                visible: false,
                searchable: false
            }
        ],
		rowCallback: function(row, data, index) {
			function stars(v) {
				var ret = '';
				for(var i = 0; i < Math.round(v); i++) {
					ret += '<i class="fa fa-star text-primary"></i>';
				}
				for(var i = Math.round(v); i < 5; i++) {
					ret += '<i class="fa fa-star-o text-primary"></i>';
				}
				return ret;
			}

            var v = $("#userlist").parents('.panel-body').width() * .8;
			for(var i = 2; i < hidden; i++) {
				$("td:eq("+i+")", row).html(stars(data[i]));
                //$("td:eq("+i+")", row).html('<progress style="max-width: '+(v / data.length)+'px" max="5.0" value="'+data[i]+'"></progress>');
			}
		}
	});

    var currentUList = [USERNAME];
    
    var mapUV = { };

    function transpose(arr, inner) {
        var newArr = [];
        
        for(var i = 0; i < inner; i++) {
            var inarr = [];
            for(var j = 0; j < arr.length; j++) {
                inarr.push(arr[j][i]);
            }
            newArr.push(inarr);
        }

        return newArr;
    }

    $(document).on('click', '.objselect', function() {
        var id = $(this).attr('id');   
        var o = id.split('-');
        var old = $('.btn-success');
        old.removeClass('btn-success');
        old.addClass('btn-default');
        $(this).removeClass('btn-default');
        $(this).addClass('btn-success');        
        table_href = "/table_data/?course="+coursename+'&task='+taskname+'&objective='+o[1];         
        table.ajax.url(table_href).load();    
    });

    $('#userlist tbody').on('click', 'tr', function() {
        var d = table.row(this).data();
        if($(this).hasClass('bg-info')) {
            unselectRow($(this), d);
        } else {
            selectRow($(this), d);
        }

        if(currentUList.length > 0) {
            var current = [skillvals];
            var s = 0;
            for(var u in mapUV) {
                var inner = [];
                for(var i = 0; i < mapUV[u].length; i++) {
                    s = mapUV[u].length;
                    inner[i] = mapUV[u][i];
                }
                current.push(inner);
            }

            var variance = getVariance(transpose(current, s));
            $("#groupvar").text(Math.round(variance * 100) / 100);
            
            if($(this).hasClass('bg-info')) {
                var notify = $("<li>").addClass("list-group-item");
                if(variance >= 2.5) {
                    notify.addClass('list-group-item-success')
                        .text("Well done. That's a good group");
                } else if(variance >= 2.0 && variance < 2.5) {
                    notify.addClass("list-group-item-warning")
                        .text("Try to raise it a bit");
                } else if(variance < 2.0) {
                    notify.addClass("list-group-item-danger")
                        .text("Low variance, this will affect your reputation");
                }
                $('#notifications .footer').before(notify);
            }
        
        } else {
            $("#groupvar").text(0.0);
        }
    });

    $('#reset').on('click', function() {
        table.order([hidden, "desc"]).draw();
    });

    $(document).on('click', '.remove i', function() {
        var id = $(this).parent().attr('id');
        $('.row_'+id).removeClass('bg-info');
        $(this).parent().remove();
        delete mapUV[id];
        currentUList.splice(currentUList.indexOf(id), 1);
        getDataDrawRadar(currentUList);
    });

    $(document).on('click', "#submitgroup", function() {
        var gname = $("#gname input").val();
        if(gname.length == 0) {
            alert("Please enter a group name");
            return;
        }
        if(currentUList.length < 2) {
            alert("You need a group size of at least 2");
            return;
        }
        var ns = [];
        for(var i in currentUList) {
            ns.push(currentUList[i].toLowerCase());
        }
        var href = "/create_group/?course="+coursename+"&task="+taskname+"&group="+JSON.stringify(ns)+"&name="+gname;
        window.location.href = href;
    });

    function unselectRow(select, d) {
        var v = d[0];
        delete mapUV[v];
        currentUList.splice(currentUList.indexOf(v), 1);
        select.removeClass('bg-info');
        $('#'+v).remove();
        getDataDrawRadar(currentUList);
    }

    function selectRow(select, d) {
        var v = d[0];
        if(currentUList.length == 4)
            return;
        mapUV[v] = d.slice(2, hidden);
        currentUList.push(v);
        select.addClass('bg-info');
        select.addClass('row_'+v);
        $("<li>")
            .addClass("list-group-item")
            .addClass("remove")
            .attr('id', v)
            .html(v + "<i class='ralign fa fa-times' style='cursor: pointer'></i>")
                .insertAfter("#litem_me");
        getDataDrawRadar(currentUList);
    }

    function getAverage(values) {
        if(values.length == 0)
            return 0;
        var sum = 0;
        for(var i in values)
            sum += values[i];
        return sum / values.length;
    }

    function getVariance(scores) {
        function _getVariance(values) {
            var avg = getAverage(values);
            var devsum = 0;
            for(var s in values) 
                devsum += Math.pow(values[s] - avg, 2);
            return devsum / values.length;
        }

        var s = 0;
        for(var i in scores) {
            s += _getVariance(scores[i]);
        }
        return s / scores.length;
    }

    function getDataDrawRadar(ulist) {
        $.ajax({
            url: '/chart_data/',
            type: 'get',
            data: { users: JSON.stringify(ulist), task: taskname },
            success: drawRadar
        });
    }

    function drawRadar(data) {
        var radarw = $("#radarchart").width() * .8,
            radarh = radarw,
            mcfg = {
                radius: 5,
                w: radarw,
                h: radarh,
                factorLegend: .4,
                ToRight: 0,
                maxValue: 1.0,
                levels: 6,
                opacityArea: 0.3,
                ExtraWidthX: radarw * .1,
                ExtraWidthY: radarh * .1,
                TranslateX: radarw * .1,
                TranslateY: radarh * .1
            };
        $("#radarchart").height(radarh * 1.2);
        RadarChart.draw("#radarchart", data, mcfg);
    }

    getDataDrawRadar(currentUList);

});
