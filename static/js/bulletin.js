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
            selectRow($(this), d[0]);
        } else {
            unselectRow($(this), d[0]);
        }
    });

    $(document).on('click', '.remove', function() {
    });

    function selectRow(select, v) {
        currentUList.splice(currentUList.indexOf(v), 1);
        select.removeClass('bg-info');
        $('#'+v).remove();
        getDataDrawRadar(currentUList);
    }

    function unselectRow(select, v) {
        currentUList.push(v);
        select.addClass('bg-info');
        $("<a>")
            .addClass("list-group-item")
            .addClass("remove")
            .attr('id', v)
            .text(v)
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
                ExtraWidthY: 0,
                TranslateX: radarw * .1,
                TranslateY: 0
            };
        RadarChart.draw("#radarchart", data, mcfg);
    }

    getDataDrawRadar(currentUList);

});
