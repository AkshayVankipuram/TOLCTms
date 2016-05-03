# TMSPrj #
### A collaborative time management system for MOOCs ###

### Installation ###
#### 1. Install django globally (requires root permissions on Linux) ####
```
$ pip install django
```
#### 2. Run manage.py ####
```
$ python manage.py runserver
```
#### 3. Launch http://localhost:8000 in the browser ####

### or ###
#### Ignore the installation steps and goto http://54.86.86.30:8080 ####

### Usage ###
#### Subset of logins available ####
| Username  | Password |
|-----------|----------|
akshay    	| akshaypass 
harshal		| harshalpass
bhargavi	| bhargavipass
ajith		| ajithpass
brock       | brockpass
aja         | ajapass
***The database has 1003 users. So for more logins you can use any of the user names (lower case) with 'pass' appended for the password.***
#### The succeeding sections explain usage as a logical flow. This is the simplest path to using all the features available. ####

**Login to Dashboard View**
 1. Interact with the tasks on the calendar by clicking on them.
 2. On the right hand side of the screen there is a Links panel. The orange colored links are new tasks and green colored links are links to the feedback for a completed task.
 3. For each course you can set the objective by clicking on the coursename on the left bottom panel and setting the objective to anything else.
 4. Click on the orange colored link. This takes you to the bulletin board.
 
**Form a group in the bulletin board**
 1. The objectives from the previous view are displayed on top of the table with your selection for the course highlighted.
 2. These serve as a filter and reduce the total number of students being displayed on the table. Click on any objective to affect filtering.
 3. Clicking on the column headers on the table will sort the table by that attribute. If you click on the **Reset Ordering** button on the left of the objective filters, the table ordering will be reset to the default hidden variance.
 4. Click on a user to add them to the group. The current group member names are displayed in the panel on the bottom right and clicking on the *x* near their name will remove them from the group.
 5. When a new member is added the chart on the top right panel is updated to show their skills and reputation compared to the other users in your group including youself.
 6. The group variance number over the group composition panel will update to reflect the current quality of your group. The notifications panel on the right bottom should update you on the quality by variance of your group.
 7. When you are ready to submit the group (4 members at most), give the group a name. Unique names only and hit submit. You will return to the dashboard view.

**Add tasks for your group**
 1. Your name is highlighted in blue for each group of which you are a member. Clicking on one or more of the cells in the column will create a dialog box that allows you to enter the title, description of the new skill along with the task tags that you believe the sub skill falls under.
 2. On the panel at the bottom right there a list of suggested tasks for each group task. These can eb dragged and dropped but the **functionality is limited and it can be dropped on any user rather than just the one you are logged in as**.
 3. You can complete a task by clicking on it and them the complted button on the overview panel.
 4. For each main task that is completed a feedback link in green will appear in the links bar on the right.
 5. Click the link to go to the feedback view.

**Peer Feedback**
 1. For each member of your group please click on the ratings to give them their feedback scores. Hit submit when done. When the final group member has been reviewed the view will revert to the dashboard view.

 #### NOTE: We have included a video of usage of the app. In it we did not create a new group or complete the feedback since we wanted you to have the option if you chose my username but you can do both those things. There is also a video of an explanation in Piazza. The video we've added to the repo is under the videos folder and it was created using Camtasia. Since it was a free trial there is gigantic watermark on the video but we felt it serves its purpose. ####