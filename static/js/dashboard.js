$(function() {

    $('.lvl').on('change', function() {
        var rating = +$(this).val();
        var id = $(this).attr("id").split("slider_")[1];
        $('#rating_'+id).text(rating);
    });


    var calContainer = $("#cal_holder");

    function refetch() {
        calContainer.fullCalendar('refetchResources');
        calContainer.fullCalendar('refetchEvents');
    }

    calContainer.fullCalendar({
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        aspectRatio: (screen.availWidth) / (screen.availHeight),
        header: {
            left: 'today prev,next',
            center: 'title',
            right: 'timelineDay,timelineWeek,month'
        },
        defaultView: 'timelineWeek',
        allDayDefault: false,
        businessHours: false,
        selectable: true,
        selectHelper: true,
        select: function(start, end, js, v, res) {
            if(res !== undefined && res.editable) {
            }
            calContainer.fullCalendar('unselect');
        },
        editable: true,
        eventLimit: true,
        eventDrop: function(ce, d, rf) {
        },
        eventResize: function(ce, d, rf) {
        },
        eventClick: function(ce, js, v) {
        },
        eventRender: function(ce, js, v) {
        },
        resourceLabelText: 'Courses',
        resourceAreaWidth: '15%',
        resourceGroupField: 'course',
        resourceRender: function(res, labelTds, bodyTds) {
            if(res.id.indexOf('group_task') > -1) {
                labelTds.addClass('bg-success');
                bodyTds.addClass('bg-success');
            } else if(res.id == USERNAME) {
                labelTds.addClass('text-primary');
            }
        },
        resources: {
            url: '/resource_stream/'
        },
        events: {
            url: '/event_stream/'
        }
    });
		
	refetch();

    setInterval(function() {
        refetch();
    }, 10 * 60 * 1000);
});
