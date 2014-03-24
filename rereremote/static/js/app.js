'use strict';

function getSetting(name, defaultVal) {
   var val = localStorage.getItem(name);
   if (val === null) {
      return defaultVal;
   }
   try {
      return JSON.parse(val);
   } catch (e) {
      if (typeof(console) !== "undefined")
         console.log("Error parsing setting '" + name + "': " + val);
      return defaultVal;
   }
}

function setSetting(name, value) {
   localStorage.setItem(name, JSON.stringify(value));
}

var app = angular.module('rereremote', []);

var ws = null;

app.controller('RootCtrl', function($scope, $rootScope) {
   $scope.page = "auth";

   $scope.switchPage = function(newPage) {
      $scope.page = newPage;
   }
});

app.controller('LoginCtrl', function($scope, $rootScope) {
   $scope.password = getSetting("rereremote.password", "");
   $scope.remember = getSetting("rereremote.remember", true);

   $scope.connecting = false;

   $scope.alert = {
      "show": false,
      "class": "warning",
      "message": ""
   };

   $scope.wsOnMessage = function(e) { $scope.$apply(function() {
      var msg = e.data;
      $scope.alert.show = false;
      if (msg == "Access granted") {
         $scope.connecting = false;
         $scope.onSuccess();
      } else if (msg == "Access denied") {
         $scope.connecting = false;
         $scope.alert = {
            'show': true,
            'class': 'warning',
            'message': "Access denied."
         };
      } else {
         $scope.connecting = false;
         $scope.alert = {
            'show': true,
            'class': 'danger',
            'message': "The server is broken."
         };
      }
   }); }

   $scope.wsOnError = function(e) { $scope.$apply(function() {
      $scope.connecting = false;
      $scope.alert = {
         'show': true,
         'class': 'danger',
         'message': "Connection failed. Please retry."
      };
   }); }

   $scope.onSuccess = function() {
      // Save the desire to remember passwords
      localStorage.setItem("rereremote.remember", $scope.remember);
      
      // Save the password, if desired
      if ($scope.remember) {
         setSetting("rereremote.password", $scope.password);
      } else {
         setSetting("rereremote.password", "");
      }

      // Unbind onmessage (no messages should be show in this page anymore)
      ws.onmessage = function() {}

      // Switch to control page
      $scope.switchPage("control");
   }

   $scope.connect = function() {
      $scope.connecting = true;
      ws = new WebSocket('ws://' + location.host + '/control?key=' +
         encodeURIComponent($scope.password));
      ws.onmessage = $scope.wsOnMessage;
      ws.onerror = $scope.wsOnError;
   }
});

app.controller('ControlCtrl', function($scope, $rootScope) {
   $scope.vibrate = function() {
      if ("vibrate" in navigator) {
         navigator.vibrate(5);
      }
   };

   $scope.previous = function() {
      ws.send("prev");
   };
   $scope.next = function() {
      ws.send("next");
   };

   $scope.alert = {
      "show": false,
      "class": "warning",
      "message": ""
   };

   $scope.disconnected = false;

   $scope.wsOnError = function() { $scope.$apply(function() {
      $scope.alert = {
         "show": true,
         "class": "danger",
         "message": "Connection with server was lost"
      };
      $scope.disconnected = true;
   }); };

   $scope.reconnect = function() {
      $scope.switchPage("auth");
   }

   ws.onerror = $scope.wsOnError;
   ws.onclose = $scope.wsOnError;
});
