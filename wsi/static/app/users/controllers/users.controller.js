(function ($, bootbox) {
  'use strict';

  angular
    .module('wsi.users.controllers', [])
    .controller('UserController', UserController);

  UserController.$inject = ['$http', '$q'];

  function UserController($http, $q) {
    var vm = this;

    vm.users = [];
    vm.filterText = '';
    vm.export = [
      {checked: true, label: 'Email'},
      {checked: true, label: 'Nick Name'},
      {checked: true, label: 'City'},
      {checked: true, label: 'Phone'},
      {checked: true, label: 'Receiving Email'},
      {checked: true, label: 'Receiving Push'},
      {checked: true, label: 'Receiving SMS'},
      {checked: true, label: 'Signature'}
    ];

    vm.filterUsers = filterUsers;
    vm.export_users = export_users;
    vm.delete_user = delete_user;
    vm.report_block = report_block;
    vm.clickCheckbox = function () {
      console.log('here');
    };

    activate();

    function activate() {
      retrieve_users();

      $('input.icheck-1').iCheck({
        checkboxClass: 'icheckbox_square-blue'
      });
    }

    function retrieve_users() {
      $http.get('/users/?type=json').then(
        function (response) {
          vm.users = response.data.users;
        },
        function (data, status, headers, config) {
          console.error('Failed to fetch user list');
        }
      );
    }

    function filterUsers() {
      return vm.users.filter(
        function (item) {
          return (
            item.email.toLowerCase().indexOf(vm.filterText.toLowerCase()) > -1 ||
            item.display_name.toLowerCase().indexOf(vm.filterText.toLowerCase()) > -1 ||
            item.city.toLowerCase().indexOf(vm.filterText.toLowerCase()) > -1
          );
        }
      );
    }

    function export_users() {
      var key_list = [];

      $('input.icheck-1').each(function () {
        if ($(this).get(0).checked) {
          key_list.push(vm.export[$(this).attr('vid') * 1].label);
        }
      });

      $("#export_keys").attr('value', JSON.stringify(key_list));
      $("#hidden_export_form").submit();
    }

    function get_user_index(user_id) {
      var ret_index = -1;
      for (var i = 0; i < vm.users.length; i++) {
        if (vm.users[i]._id == user_id) {
          ret_index = i;
          break;
        }
      }
      return ret_index;
    }

    function report_block(user_id) {
      bootbox.dialog({
        message: "Are you sure to block this user?",
        title: "Block it",
        buttons: {
          danger: {
            label: "Block It!",
            className: "btn-danger",
            callback: function () {
              var user_index = get_user_index(user_id);
              var user = vm.users[user_index];

              $http.post('/blacklist/', user).then(
                function (response) {
                  vm.users[user_index].is_blocked = true;
                },
                function (error) {
                }
              );
            }
          }
        }
      });
    }

    function delete_user(user_id) {
      bootbox.dialog({
        message: "Are you sure to delete this user?<br/><span class='label label-warning'>It will delete user data!</label>",
        title: "Delete User",
        buttons: {
          danger: {
            label: "CONFIRM",
            className: "btn-success",
            callback: function () {
              var user_index = get_user_index(user_id);
              var user = vm.users[user_index];
              $http.post('/users/', {user: user, method: 'delete', type: 'json'})
                .then(
                  function (response) {
                    vm.users.splice(user_index, 1);
                  },
                  function (error) {
                  }
                );
            }
          }
        }
      });
    }
  }
})($, bootbox);
