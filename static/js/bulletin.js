var table = null;
$(function () {

    var href = "/table_data/?course="+coursename+'&task='+taskname;

	table = $("#userlist").DataTable({
		ajax: href,
		responsive: true,
		autoWidth: false,
		lengthMenu: [ 20, 40 ],
		rowCallback: function(row, data, index) {
			function stars(v) {
				var ret = '';
				for(var i = 0; i < Math.round(v); i++) {
					ret += '<i class="fa fa-star"></i>';
				}
				for(var i = Math.round(v); i < 5; i++) {
					ret += '<i class="fa fa-star-o"></i>';
				}
				return ret;
			}

			for(var i = 2; i <= 8; i++) {
				$("td:eq("+i+")", row).html(stars(data[i]));
			}
		}
	});

	$(table.column(9).nodes()).addClass("bg-success");
  
    var currentUList = [];

    $('#userlist tbody').on('click', 'tr', function() {
        var d = table.row(this).data();
        if($(this).hasClass('bg-info')) {
            unselectRow($(this), d[0]);
        } else {
            selectRow($(this), d[0]);
        }
    });

    $(document).on('click', '.remove i', function() {
        var id = $(this).parent().attr('id');
        $('.row_'+id).removeClass('bg-info');
        $(this).parent().remove();
    });

    function unselectRow(select, v) {
        currentUList.splice(currentUList.indexOf(v), 1);
        select.removeClass('bg-info');
        $('#'+v).remove();
        getDataDrawRadar(currentUList);
    }

    function selectRow(select, v) {
        if(currentUList.length == 5)
            return;
        currentUList.push(v);
        select.addClass('bg-info');
        select.addClass('row_'+v);
        $("<li>")
            .addClass("list-group-item")
            .addClass("remove")
            .attr('id', v)
            .html(v + "<i class='ralign fa fa-times' style='cursor: pointer'></i>")
                .insertBefore(".group .footer");
        getDataDrawRadar(currentUList);
    }

    function getDataDrawRadar(ulist) {
        $.ajax({
            url: '/chart_data/',
            type: 'get',
            data: { users: JSON.stringify(ulist) },
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
