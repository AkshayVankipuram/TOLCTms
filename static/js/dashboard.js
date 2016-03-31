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
                createModal(
                    $("<h3>").text("New Event"),
                    $("<div>").addClass("form-group")
                        .append("<p hidden id='eresid'>"+res.id+"</p>")
                        .append("<p hidden id='estart'>"+start.toISOString()+"</p>")
                        .append("<p hidden id='eend'>"+end.toISOString()+"</p>")
                        .append($("<code>").text(start.toString()))
                        .append("<br>")
                        .append($("<code>").text(end.toString()))
                        .append("<br>")
                        .append($("<label>").attr("for", "etitle").text("Title"))
                        .append($("<input>").attr("id", "etitle").addClass("form-control"))
                        .append("<br>")
                        .append($("<label>").attr("for", "edesc").text("Description"))
                        .append($("<textarea>").attr("id", "edesc").addClass("form-control")), 
                    $("<button>").addClass("btn btn-default").attr("id","esubmit").text("Submit")
                );
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
            var div = $("<div>");
            var strs = ce.description.split(".");
            for(var i in strs) {
                div.append($("<p>").text(strs[i]));
            }
            createModal(
                    $("<h3>").text(ce.title),
                    div,
                    ""
            );
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

    
    function createModal(title, body, footer) {
        var tmpl = $("#modalTmpl");
        $(".mh", tmpl).html(title);
        $(".mb", tmpl).html(body);
        $(".mf", tmpl).html(footer);
        tmpl.modal("show");
    }

    $(document).on("click", "#esubmit", function() {
        calContainer.fullCalendar("renderEvent", {
            title: $("#etitle").val(),
            description: $("#edesc").val(),
            resourceId: $("#eresid").text(),
            start: $("#estart").text(),
            end: $("#eend").text()
        }, true);
        $("#modalTmpl").modal("hide");
    });

});
