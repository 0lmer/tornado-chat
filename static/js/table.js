'use strict';

var pokerApp = angular.module('pokerApp', ['ngRoute', 'ngAnimate']);//angucomplete

pokerApp.controller('roomCtrl', function($scope, $http, socketFactory, table) {
    $scope.table = table;
    $scope.gamers = [];

    $scope.setSessionSid = function(sid) {
        socketFactory.setSessionSid(sid);
    };

    $scope.join = function() {
        socketFactory.join($scope.table._id);
    };

    $scope.init = function() {
        socketFactory.connect();
        socketFactory.onmessage(function(message) {
            var messageData = JSON.parse(message.data);
            switch(messageData.type) {
                case 'hand_cards':
                    break;
                case 'board_cards':
                    break;
                case 'bets':
                    break;
                case 'table':
                    switch(messageData.action) {
                        case 'join':
                            $scope.wsController.joinedTable(messageData.data.gamer);
                            break;
                        case 'leave':
                            $scope.wsController.leavedTable(messageData.data.gamer);
                            break;
                    }
                    break;
            }
        });

        $scope.wsController = {
            joinedTable: function(gamer) {
                $scope.$apply(function() {
                    $scope.gamers.push(gamer);
                    console.log('Gamer ' + gamer.name + ' joined.');
                });
            },
            leavedTable: function(gamer) {
                $scope.$apply(function() {
                    for (var idx in $scope.gamers) {
                        if ($scope.gamers[idx].login === gamer.login) {
                            $scope.gamers.splice(idx, 1);
                            console.log('Gamer ' + gamer.name + ' left.');
                            break;
                        }
                    }
                });
            }
        }
    };

    $scope.init();
});


pokerApp.factory('socketFactory', function() {
    var service = {};
    var ws_url = 'http://' + document.location.host + '/poker/ws';
    var ws_options = {
        'protocols_whitelist': ['websocket', 'xdr-streaming', 'xhr-streaming', 'iframe-eventsource',
        'iframe-htmlfile', 'xdr-polling', 'xhr-polling', 'iframe-xhr-polling', 'jsonp-polling']
    };
    var ws;
    var session_sid = '';
    var connection = false;

    var wsSend = function(messageObj) {
        messageObj['sid'] = session_sid;

        var msg = JSON.stringify(messageObj);
        ws.send(msg);
    };

    service.connect = function() {
        ws = new SockJS(ws_url, null, ws_options);
        ws.onmessage = function (message) {
        };

        ws.onclose = function () {
            console.log('connection closed');
            var onMessageCallback = ws.onmessage;
            setTimeout(function() {
                service.connect();
                service.onmessage(onMessageCallback);
            }, 2000);
        };
        ws.onopen = function () {
            console.log('connection open');
            connection = true;
        };
    };

    service.disconnect = function() {
        ws.close();
    };

    service.join = function (tableId) {
        wsSend({ type: 'table', action: 'join', data: { table_id: tableId } });
    };

    service.raise = function(amount) {
        wsSend({type:'raise', amount: amount});
    };

    service.call = function() {
        wsSend({type: 'call'});
    };

    service.check = function() {
        wsSend({type: 'check'});
    };

    service.fold = function() {
        wsSend({type: 'fold'});
    };

    //service.sendMessage = function(chatRoom, message) {
    //    wsSend({type:'message', room: chatRoom, text: message});
    //};
    //
    //service.joinToChat = function(chatRoom) {
    //    wsSend({type: 'join', 'room': chatRoom});
    //};
    //
    //service.leaveChat = function(chatRoom) {
    //    wsSend({type: 'leave', room: chatRoom});
    //};

    service.getMessages = function() {
        return messages;
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