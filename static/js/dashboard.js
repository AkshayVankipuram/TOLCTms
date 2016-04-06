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
            right: 'timelineWeek,month'
        },
        defaultView: 'timelineWeek',
        allDayDefault: false,
        businessHours: false,
        droppable: true,
        drop: function(date, j, u, r) {
            $(this).remove();
        },
        selectable: true,
        selectHelper: true,
        select: function(start, end, js, v, res) {
            if(res === undefined || (res !== undefined && res.editable)) {
                var form = $("<div>").attr('role', "form");
                var tags = '<div class="well well-sm">';
                for(var t in tasktags) {
                    tags += "<kbd id='"+tasktags[t].replace(/ /g, '_')+"'>" + tasktags[t] + "</kbd>  ";
                }
                tags += "</div>";
                createModal(
                    $("<h3>").text("New Event"),
                    form.append("<p hidden id='eresid'>"+USERNAME+"</p>")
                        .append("<p hidden id='estart'>"+start.toISOString()+"</p>")
                        .append("<p hidden id='eend'>"+end.toISOString()+"</p>")
                        .append($("<code>").text('Start: '+start.toString()))
                        .append("<br><br>")
                        .append($("<code>").text('End: '+end.toString()))
                        .append("<br><br>")
                        .append($("<div>").addClass("form-group")
                            .append(tags)
                            .append($("<label>").attr("for", "etitle").text("Title"))
                            .append($("<input>")
                                .attr("id", "etitle")
                                .addClass("form-control")))
                        .append($("<div>").addClass("form-group")
                            .append($("<label>").attr("for", "edesc").text("Description"))
                            .append($("<textarea>")
                                .css('resize','none')
                                .attr("id", "edesc")
                                .attr('rows', 5)
                                .addClass("form-control"))),
                    $("<button>").addClass("btn btn-default").attr('type', 'submit').attr("id","esubmit").text("Submit")
                );
            }
            calContainer.fullCalendar('unselect');
        },
        editable: true,
        eventLimit: true,
        eventDrop: function(ce, d, rf) {
            if(ce.resourceId != USERNAME) {
                rf();
            }
        },
        eventResize: function(ce, d, rf) {
        },
        eventClick: function(ce, js, v) {
            if(ce.completed === undefined || !ce.completed) {
                var div = $("<div>");
                strs = ce.description.split(".");
                for(var i in strs) {
                    div.append($("<p>").text(strs[i]));
                }
                createModal(
                        $("<h3>").text(ce.title),
                        div,
                        $("<button>").addClass("btn btn-default").html("Completed").on('click', function() {
                            ce.color = colorvalues.greens[3];
                            ce.completed = true;
                            calContainer.fullCalendar("updateEvent", ce);
                            $('#goto').append($('<a>')
                                .addClass('list-group-item list-group-item-success feedback')
                                .html(ce.title + '<i class="ralign fa fa-comment"></i>')
                                .attr('href', '/feedback/'));
                            $("#modalTmpl").modal("hide");
                        })
                );
            }
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

    
    function createModal(head, body, foot) {
        var tmpl = $("#modalTmpl");
        $(".modal-title", tmpl).html(head);
        $(".modal-body", tmpl).html(body);
        $(".modal-footer", tmpl).html(foot);
        tmpl.modal('show');
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

    $(document).on("click", "kbd", function() {
        var tag = $(this).attr('id').replace(/_/g, ' ');
        $(this).toggleClass('bg-primary');
    });

    $(document).on('click', '.objselect', function() {
        var id = $(this).attr('id');
        var e = id.split('-');
        var course = e[0].replace(/_/g,' ');
        var href = '/set_objective/?course='+course+'&objective='+e[1];
    });
    
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
        RadarChart.draw("#radarchart", [data], mcfg);
    }

    $.ajax({
        url: '/chart_data/',
        type: 'get',
        data: { tp: 'useronly' },
        success: drawRadar
    });

    function setupTaskBreakdown(data) {
        var root = $("#suggested");
        for(var task in data) {
            root.append($("<li>")
                    .addClass("list-group-item list-group-item-info")
                    .text(task));
            var li = $("<li>").addClass("list-group-item");
            $.each(data[task], function(idx, v) {
                li.append($("<div>")
                    .addClass("fc-event extern")
                    .text(v.title)
                    .data('event', v)
                    .draggable({
                        zIndex: 999,
                        revert: true,
                        revertDuration: 10
                    }));
            });
            root.append(li);
        }
    }

    $.ajax({
        url: '/get_skill_breakdown/',
        type: 'get',
        success: setupTaskBreakdown
    });

});
