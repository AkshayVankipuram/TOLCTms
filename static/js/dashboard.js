$(function() {

	check($('#icon_'+PREFSKILL1.name));
	check($('#icon_'+PREFSKILL2.name));
	check($('#icon_'+PREFSKILL3.name));

	$("#slider_"+PREFSKILL1.name).val(PREFSKILL1.level);
	$("#slider_"+PREFSKILL2.name).val(PREFSKILL2.level);
	$("#slider_"+PREFSKILL3.name).val(PREFSKILL3.level);

	$("#slider_"+PREFSKILL1.name).attr('disabled', false);
	$("#slider_"+PREFSKILL2.name).attr('disabled', false);
	$("#slider_"+PREFSKILL3.name).attr('disabled', false);

	var max_selected = 3;
	var current_skills = {};
	current_skills[PREFSKILL1.name] = PREFSKILL1.level;
	current_skills[PREFSKILL2.name] = PREFSKILL2.level;
	current_skills[PREFSKILL3.name] = PREFSKILL3.level;

	$(".skillcheckicon").on('click', function() {
		var skill = $(this).attr('id').split('_')[1];
		if($(this).hasClass('checked')) {
			uncheck($(this));
			if(skill in current_skills)
				delete current_skills[skill];
			$("#slider_"+skill).val(0);
			$("#slider_"+skill).attr('disabled', true);
			max_selected --;
		} else if(max_selected < 3) {
			check($(this));	
			current_skills[skill] = 0;
			$("#slider_"+skill).attr('disabled', false);
			max_selected ++;
		}
		save_skills(current_skills);
		$('#selnum').text(max_selected);
	});

	$('.lvl').on('change', function() {
		var skill = $(this).attr('id').split('_')[1];
		if(skill in current_skills) {
			current_skills[skill] = $(this).val();
		}
		save_skills(current_skills);
	});

	function uncheck($icon) {
		$icon.removeClass('fa-check');
		$icon.addClass('fa-times');
		$icon.removeClass('checked');
	}

	function check($icon) {
		$icon.removeClass('fa-times');
		$icon.addClass('fa-check');
		$icon.addClass('checked');
	}

	function save_skills(list) {
		$.ajax({
			url: '/save_skills/',
			type: 'GET',
			data: {
				skills: JSON.stringify(list)
			}
		});
	}

});