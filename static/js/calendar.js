$(function() {

    var calContainer = $("#cal_holder");

    var LOGGED_USERS = [];

    $('#eventCreate').modal({
        show: false,
        keyboard: false,
        backdrop: 'static'
    });

    $('#eventView').modal({
        show: false,
    });

    var evtObj = {
        id: '',
        resourceId: USERNAME,
        title: '',
        decription: '',
        start: '',
        end: '',
        editable: true,
        parent: '',
        children: [],
        color: '',
    };

    var currentEvt = null;
    var toDeleteEvent = '';

    function refetch() {
        $.getJSON('/logged_users/', function(ulist) {
            LOGGED_USERS = ulist;
            calContainer.fullCalendar('refetchResources');
            calContainer.fullCalendar('refetchEvents');
        });    
    }

    calContainer.fullCalendar({
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        aspectRatio: (screen.availWidth * 0.9) / (screen.availHeight),
        header: {
            center: 'title',
            left: 'today',
            'right': 'timelineCustom'
        },
        views: {
            timelineCustom: {
                type: 'timeline',
                duration: {
                    days: 10
                }
            }
        },
        defaultView: 'timelineCustom',
        allDayDefault: false,
        businessHours: false,
        selectable: true,
        selectHelper: true,
        select: function(start, end, js, v, res) {
            if(res.title != USERNAME) {
                calContainer.fullCalendar('unselect');
                return false;
            }
            $('#eventCreate').modal('show');
            currentEvt = Object.create(evtObj);
            currentEvt.start = start;
            currentEvt.end = end;
            calContainer.fullCalendar('unselect');
        },
        editable: true,
        eventLimit: true,
        eventDrop: function(ce, d, rf) {
            if(ce.resourceId != USERNAME) {
                rf();
                return false;
            }
            /*$.getJSON('/save_event/?event='+JSON.stringify({
                id: ce.id,
                title: ce.title,
                description: ce.description,
                start: ce.start,
                end: ce.end,
                editable: ce.editable,
                parent: ce.parent,
                children: ce.children,
                color: encodeURIComponent(ce.color)
            }));*/
        },
        eventResize: function(ce, d, rf) {
            /*$.getJSON('/save_event/?event='+JSON.stringify({
                id: ce.id,
                title: ce.title,
                description: ce.description,
                start: ce.start,
                end: ce.end,
                editable: ce.editable,
                parent: ce.parent,
                children: ce.children,
                color: encodeURIComponent(ce.color)
            }));*/
        },
        eventClick: function(ce, js, v) {
            /*if(calContainer.fullCalendar('clientEvents', ce._id)[0].editable) {
                $("#eventDelete").css('display','block');
            } else {
                $("#eventDelete").css('display','none');
            }
            toDeleteEvent = ce._id;*/
            createEventView(ce);
        },
        resourceLabelText: 'Group',
        resourceAreaWidth: '15%',
        resourceGroupField: 'group',
        resourceRender: function(res, labelTds, bodyTds) {
            if(res.title == USERNAME) {
                labelTds.css("background", res.eventColor);
                labelTds.css("color", 'white');
            }
            
            if(LOGGED_USERS.indexOf(res.title) >= 0) {
                var h = labelTds.html().replace(res.title, 
                        res.title + 
                        '&nbsp;<code><small>on</small></code>');
                labelTds.html(h);
            } else if(res.title != 'Course Tasks' && res.title != USERNAME) {
                var h = labelTds.html().replace(res.title, 
                        res.title + 
                        '&nbsp;<code><small>off</small></code>');
                labelTds.html(h);
            }
        },
        resources: {
            url: '/resource_stream/'
        },
        events: {
            url: '/event_stream/'
        }
    });

    $(document).on('click', '#eventCreate .close', function() {
        delete currentEvt;
    });

    $(document).on('click', '#eventSubmit', function() {
        currentEvt.title = $("#eventTitle").val();
        currentEvt.desc = $("#eventDesc").val();
        currentEvt.id = currentEvt.title.replace(/ /g, '_');
        var parent = $("#subtask_select option:selected").text();
        
        if(parent != "None")
            currentEvt.parent = parent;

        var parentEvt = getEventParent(currentEvt);
        if(!isSubevent(parentEvt, currentEvt)) {
            setError('Cannot create child event outside parent time period');
        } else {
            if(parentEvt != null) {
                currentEvt.constraint = parentEvt.id;
                parentEvt.children.push(currentEvt.title);
                calContainer.fullCalendar('updateEvent', parentEvt);
            }
            
            setError('');
            calContainer.fullCalendar('renderEvent', currentEvt, true);
            
            $("#subtask_select").append('<option class="'+currentEvt.id+'">'+currentEvt.title+'</option>');
            
            $('#eventCreate').modal('hide');
            
            $.getJSON('/save_event/?event='+JSON.stringify(currentEvt));

            delete currentEvt;
         
            resetEventCreateModal();
        }
    });

    function resetEventCreateModal() {
        $('#eventTitle').val('');
        $('#eventDesc').val('');
    }

    function setError(msg) {
        $("#eventCreate .err_msg").text(msg);
    }

    function createEventView(ce) {
        $('#eventContent').empty();
        $('#eventContent')
            .append($('<li>').addClass('list-group-item active').text('Title'))
            .append($('<li>').addClass('list-group-item').text(ce.title))
            .append($('<li>').addClass('list-group-item active').text('Description'))
            .append($('<li>').addClass('list-group-item').text(ce.description))
            .append($('<li>').addClass('list-group-item active').text('Start'))
            .append($('<li>').addClass('list-group-item').text(ce.start.toString()))
            .append($('<li>').addClass('list-group-item active').text('End'))
            .append($('<li>').addClass('list-group-item').text(ce.end.toString()));
        if(ce.parent != '') {
            $('#eventContent')
                .append($('<li>').addClass('list-group-item active').text('Parent'))
                .append($('<li>').addClass('list-group-item').text(ce.parent));
        }
        $('#eventContent').append($('<li>').addClass('list-group-item active').text('Children'));
        for(var i = 0; i < ce.children.length; i++) {
            $('#eventContent').append($('<li>').addClass('list-group-item').text(ce.children[i]));
        }
        $('#eventView').modal('show');
    }


    $(document).on('click', '#eventDelete', function() {
        var e = calContainer.fullCalendar('clientEvents', toDeleteEvent)[0];
        $('#subtask_select .'+e.id).remove();
        calContainer.fullCalendar('removeEvents', toDeleteEvent);
        $('#eventView').modal('hide');
    });

    function isSubevent(parent, child) {
        if(parent == null)
            return true;
        if((child.start.isSame(parent.start) ||
            child.start.isAfter(parent.start)) &&
            (child.end.isSame(parent.end) ||
            child.end.isBefore(parent.end))) {
            return true;
        }
        return false;
    }

    function eventExists(ce) {
        var events = calContainer.fullCalendar('clientEvents');
        if(ce != null) {
            for(var i = 0; i < events.length; i++) {
                if(events[i].title == ce.title &&
                    events[i].start.isSame(ce.start) &&
                    events[i].end.isSame(ce.end)) {
                    return true;
                }
            }
        }
        return false;
    }

    function getEventParent(ce) {
        var parent = calContainer.fullCalendar('clientEvents', function(evt) {
            return evt.title == ce.parent;
        });
        return (parent.length > 0) ? parent[0] : null;
    }

    function getEventByTitle(title) {
        var cevt = calContainer.fullCalendar('clientEvents', function(evt) {
            return evt.title == title;
        });
        return (cevt.length > 0) ? cevt[0] : null;
    }

    function findDepth(e) {
        var d = 0;
        var n = e;
        while((n = getEventParent(n)) != null) {
            d++;
        }
        return (d >= 11) ? 10 : d ;
    }

    refetch();

    setInterval(function() {
        refetch();
    }, 5 * 60 * 1000);

});
