$(function() {
	
    var max_selected = 3;
	var current_skills = {};
    
    for(var i in PREFS.skills) {
        var skill = PREFS.skills[i];
        check($("#icon_"+skill.name));
	    $("#slider_"+skill.name).val(skill.level).attr('disabled', false);
        current_skills[skill.name] = skill.level;
    }


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
