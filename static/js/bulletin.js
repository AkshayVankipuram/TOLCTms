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

});
