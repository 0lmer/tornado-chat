'use strict';

var pokerApp = angular.module('pokerApp', ['ngRoute', 'ngAnimate']);//angucomplete

pokerApp.controller('pokerCtrl', function($scope, $http, socketFactory) {
    $scope.currentRoom = undefined;
    $scope.connectionStatus = chatFactory.getConnectionStatus();
    $scope.currentMessage = '';
    $scope.messages = [];
    $scope.glued = true;

    $scope.newChatRoomName = '';

    $scope.isCurrentRoom = function(room) {
        return (room == $scope.currentRoom);
    };

    $scope.setCurrentRoom = function(chatRoom) {
        chatFactory.joinToChat(chatRoom);
        $scope.currentRoom = chatRoom;
    };

    $scope.createRoom = function(chatRoom) {
        if (!chatRoom) { return; }
        if ($scope.rooms.indexOf(chatRoom) < 0) {
            $scope.rooms.push(chatRoom);
        }
        $scope.setCurrentRoom(chatRoom);
        $scope.newChatRoomName = '';
    };

    $scope.leaveRoom = function(chatRoom) {
        var index = $scope.rooms.indexOf(chatRoom);
        if (index >= 0) {
            $scope.rooms.splice(index, 1);
        }
        chatFactory.leaveChat(chatRoom);
    };

    $scope.sendMessage = function(message) {
        if (message) { chatFactory.sendMessage($scope.currentRoom, message); }
        $scope.currentMessage = '';
    };

    $scope.setSessionSid = function(sid) {
        chatFactory.setSessionSid(sid);
    };


    $scope.init = function() {
        chatFactory.connect();
        chatFactory.onmessage(function(message) {
            var data = JSON.parse(message.data);
            $scope.messages.push(data);
            $scope.$apply();
        });

        //$http.get('https://host').success(function(data) {
        //});
    };

    $scope.rooms = [];
    $scope.init();
});


pokerApp.factory('socketFactory', function(socketFactory) {
    var service = {};
    var ws_url = 'http://' + document.location.host + '/chat/ws';
    var ws;
    var session_sid = '';
    var connection = false;

    var wsSend = function(obj) {
        obj['sid'] = session_sid;

        var msg = JSON.stringify(obj);
        ws.send(msg);
    };

    service.connect = function() {
        ws = new SockJS(ws_url, null, {
                'protocols_whitelist': ['websocket', 'xdr-streaming', 'xhr-streaming', 'iframe-eventsource',
                    'iframe-htmlfile', 'xdr-polling', 'xhr-polling', 'iframe-xhr-polling', 'jsonp-polling']
        });
        ws.onmessage = function (message) {
        };

        ws.onclose = function () {
            console.log('connection closed');
            this.socket = new WebSocket(ws.url);
        };
        ws.onopen = function () {
            console.log('connection open');
            connection = true;
        };
    };

    service.disconnect = function() {
        ws.close();
    };

    service.sendMessage = function(chatRoom, message) {
        wsSend({type:'message', room: chatRoom, text: message});
    };

    service.joinToChat = function(chatRoom) {
        wsSend({type: 'join', 'room': chatRoom});
    };

    service.leaveChat = function(chatRoom) {
        wsSend({type: 'leave', room: chatRoom});
    };

    service.getMessages = function() {
        return messages;
    };

    service.getConnectionStatus = function() {
        return connection;
    };

    service.setSessionSid = function(sid) {
        session_sid = sid;
    };

    service.onmessage = function(callback) {
        callback = (callback) ? callback : function(data) { };
        ws.onmessage = callback;
    };

    return service;
});

pokerApp.factory('urlFactory', function() {
    var protocolRegexp = new RegExp("^(ht|f)tp(s?)\:\/\/");

    return {
        fixProtocolIfNeeded: function(url) {
            return (url.search(protocolRegexp) < 0) ? ('http://' + url) : (url);
        },
        convertUrlToHTMLTag: function(url) {
            return '<a target="_blank" href="' + url + '">' + url + '</a>';
        }
    }
});

pokerApp.filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
}).filter('urlify', function(urlFactory) {
    return function(text) {
        var urlRegex = /(([a-z]+:\/\/)?(([a-z0-9\-]+\.)+([a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel|local|internal))(:[0-9]{1,5})?(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&amp;]*)?)?(#[a-zA-Z0-9!$&'()*+.=-_~:@/?]*)?)(\s+|$)/gi;
        return text.replace(urlRegex, function(url) {
            return urlFactory.convertUrlToHTMLTag(urlFactory.fixProtocolIfNeeded(url));
        });
    };
});