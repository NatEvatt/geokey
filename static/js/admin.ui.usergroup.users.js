/* ***********************************************
 * Mangages the members of user groups.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

(function () {
    'use strict';

    var projectId = $('body').attr('data-project-id');
    var groupId = $('body').attr('data-group-id');

    // Get the elements
    var typeAwayResults = $('.type-away');
    var formField = $('#find-users');
    var userList = $('.user-list');

    var url;
    if (groupId) {
        url = 'projects/' + projectId + '/usergroups/' + groupId + '/users/';
    } else {
        url = 'projects/' + projectId + '/admins/';
    }

    var numberOfRequests = 0;

    /**
     * Handles the click event when the user clicks on the remove link in the user list.
     * @param  {Event} event The click event fired by the link.
     */
    function handleRemoveUser(event) {
        var userId = $(event.target).parent('a').attr('data-user-id');
        var itemToRemove = $(event.target).parents('li');

        /**
         * Handles the response after the removal of the user from the group was successful.
         */
        function handleRemoveUserSuccess() {
            var html = $('<li class="bg-success message"><span class="text-success"><span class="glyphicon glyphicon-ok"></span> The user has been removed from the user group.</span></li>');
            itemToRemove.before(html);
            setTimeout(function() {html.remove(); }, 5000);

            itemToRemove.remove();

            var numOfUsers = userList.children(':not(.message)').length;

            if (!groupId &&  numOfUsers === 1) {
                userList.find('li a.remove').remove();
            }

            if (numOfUsers === 0) {
                userList.append('<li class="empty">No users have been assigned to this group.</li>');
            }
        }

        /**
         * Handles the response after the removal of the user from the group failed.
         * @param  {Object} response JSON object of the response
         */
        function handleRemoveUserError(response) {
            var html = $('<li class="bg-danger message"><span class="text-danger"><span class="glyphicon glyphicon-remove"></span> An error occured while removing the user. Error text was: ' + response.responseJSON.error + '</span></li>');
            itemToRemove.before(html);
            setTimeout(function() {html.remove(); }, 5000);
        }

        Control.Ajax.del(url + userId+ '/', handleRemoveUserSuccess, handleRemoveUserError, {'userId': userId});
        event.preventDefault();
    }


    /**
     * Handles the response if the addition of the user to the group was successful.
     * @param  {Object} response JSON object of the response
     */
    function handleAddUserSucess(response) {
        userList.empty();

        if (!userList.length) {
            userList = $('<ul class="user-list"></ul>').appendTo('#members');
            $('#members .empty-list').hide();
        }

        var html = $('<li class="bg-success message"><span class="text-success"><span class="glyphicon glyphicon-ok"></span> The user has been added to the user group.</span></li>');
        userList.append(html);
        setTimeout(function() {html.remove(); }, 5000);

        userList.append(Templates.usergroupusers(response));
        userList.find('li a.remove').click(handleRemoveUser);

        formField.val('');
    }

    /**
     * Handles the response if the addition of the user to the group failed.
     * @param  {Object} response JSON object of the response
     */
    function handleAddUserError(response) {
        // displayError('An error occured while adding the user. Error text was: ' + response.responseJSON.error);
    }

    /**
     * Handles click events pn items in the user dropdown list. Adds the user to the group.
     * @param  {Event} event The click event on the user link.
     */
    function handleAddUser(event) {
        var userId = $(event.target).attr('data-user-id');

        typeAwayResults.hide();
        Control.Ajax.post(url, handleAddUserSucess, handleAddUserError, {'userId': userId});
        event.preventDefault();
    }



    /**
     * Handles the reponse the the request for the user list was successful. Updates the dropdown list.
     * @param  {Object} response JSON object of the response
     */
    function handleSuccess(response) {
        var users = response;
        var header = (users.length > 0 ? 'Click on item to add user' : 'No records matched your query');

        typeAwayResults.children().not('.dropdown-header').remove();
        numberOfRequests--;
        if (numberOfRequests === 0) {
            formField.removeClass('loading');
        }

        typeAwayResults.append(Templates.userstypeaway(response));

        typeAwayResults.children('.dropdown-header').text(header);
        typeAwayResults.find('li a').click(handleAddUser);
        typeAwayResults.show();
    }

    /**
     * Handles the reponse the the request for the user list failed.
     */
    function handleError() {
        numberOfRequests--;
        if (numberOfRequests === 0) {
            formField.removeClass('loading');
        }
        typeAwayResults.children().not('.dropdown-header').remove();
        typeAwayResults.children('.dropdown-header').html('<span class="text-danger">An error occured while trying to retrieve the user list. Please try again.</span>');
        typeAwayResults.show();
    }

    /**
     * Handles user type in the search field. Requests for a users list after 3 characters have been typed.
     * @param  {Event} event The keyup event fired by the field.
     */
    function handleFormType(event) {
        var activeLink = typeAwayResults.find('li.active');
        if (event.keyCode === 13) {
            if (activeLink.length > 0) {
                activeLink.children().click();
            }
        }
        else if ((event.keyCode === 40 || event.keyCode === 38) && typeAwayResults.is(":visible")) {
            event.preventDefault();
            if (activeLink.length > 0) {
                if (event.keyCode === 38) {
                    // move up
                    if (activeLink.prev().not('.dropdown-header').length) {
                        activeLink.removeClass('active');
                        activeLink.prev().addClass('active');
                    }
                }
                if (event.keyCode === 40) {
                    // move down
                    if (activeLink.next().length) {
                        activeLink.removeClass('active');
                        activeLink.next().addClass('active');
                    }
                }
            } else {
                typeAwayResults.find('li').not('.dropdown-header').first().addClass('active');
            }
        } else {
            if (event.target.value.length === 1) {
                typeAwayResults.hide();
            } else if (event.target.value.length >= 2) {
                formField.addClass('loading');
                numberOfRequests++;
                Control.Ajax.get('users/?query=' + event.target.value, handleSuccess, handleError);
            }
        }
    }

    // Register the click event handler of remove links
    userList.find('li a.remove').click(handleRemoveUser);

    // Register the keyup event on the text field.
    formField.keydown(handleFormType);
}());
