$(function() {

	$('.generalMetricRadio').change(function(){
		$('#generalMetricScoreDiv').html(computeScore('generalMetricEvaluationTable'));
	});
	$('.taskMetricRadio').change(function(){
		$('#taskMetricScoreDiv').html(computeScore('taskMetricEvaluationTable'));
	});

    $('#submitButton').click(function() {

		if($('#peerListDiv').find('.active').length == 0)
		{
			$("#notifications  li:eq(1)").before($("<li>")
			.addClass("list-group-item list-group-item-danger")
			.text("Please select a Peer for evaluation."));
			//alert("Please select a Peer for evaluation.");
		}
		else
		{
			var currentPeer = $('#peerListDiv').find('.active')[0];
			$("#notifications  li:eq(1)").before($("<li>")
			.addClass("list-group-item list-group-item-success")
			.text("Your evaluation for " + currentPeer.innerHTML+" has been recorded. Thank you."));
			//alert("Your evaluation for " + currentPeer.innerHTML+" has been recorded. Thank you.");
			currentPeer.remove();
			resetForm();
			
			if($('#peerListDiv').find('a').length == 0)
				window.location.href = '/home'
		}
    });
	
	$('#peerListDiv a').click(function(e) {
        e.preventDefault()
        $that = $(this);
        $('#peerListDiv').find('a').removeClass('active');
        $that.addClass('active');
    });
});


function computeScore(className)
{
	var selectedVal = "";
	var selected = $("."+className+" label.active");
	var count = 0;
	var score = 0.0;
	if (selected.length > 0) {
		selected.each(function(){
			if($(this).find('input')[0].value != 'na')
			{	
				score+= parseInt($(this).find('input')[0].value);
				count++
			}
		});
	}
	if(count > 0)
		return (score/count).toFixed(2);
	else 
		return 'NA';
}

function resetForm()
{
	$(".generalMetricEvaluationTable label.active").removeClass('active');
	$(".taskMetricEvaluationTable label.active").removeClass('active');
	
	var naGeneralLabels = $(".generalMetricEvaluationTable label").find('input[value="na"]').parent();
	naGeneralLabels.each(function(){$(this).addClass('active');});
	var naTaskLabels = $(".taskMetricEvaluationTable label").find('input[value="na"]').parent();
	naTaskLabels.each(function(){$(this).addClass('active');});
	
	$('#generalMetricScoreDiv').html('NA');
	$('#taskMetricScoreDiv').html('NA');
}
