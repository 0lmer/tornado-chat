'use strict';

var pokerApp = angular.module('pokerApp', ['ngRoute', 'ngAnimate']);//angucomplete

pokerApp.controller('roomCtrl', function($scope, $http, socketFactory, table, sid) {
    $scope.table = table;
    $scope.sid = sid;
    $scope.players = $scope.table.players;
    $scope.betAmount = 0;
    $scope.pot = 0;
    $scope.circlePot = 0;

    $scope.join = function() {
        socketFactory.join($scope.table._id);
    };

    $scope.leave = function() {
        socketFactory.leave($scope.table._id);
    };

    $scope.bet = function() {
        socketFactory.bet($scope.table._id, $scope.betAmount);
        $scope.betAmount = 0;
    };

    $scope.fold = function() {
        socketFactory.fold($scope.table._id);
    };

    $scope.init = function() {
        socketFactory.connect();
        socketFactory.setSid(sid);
        socketFactory.onmessage(function(message) {
            var messageData = JSON.parse(message.data);
            switch(messageData.type) {
                case 'table':
                    switch(messageData.action) {
                        case 'join':
                            $scope.wsController.joinedTable(messageData.data.player);
                            break;
                        case 'leave':
                            $scope.wsController.leavedTable(messageData.data.player);
                            break;

                        case 'bet':
                            $scope.wsController.bet(messageData.data.player, parseFloat(messageData.data.amount));
                            break;
                        case 'fold':
                            $scope.wsController.fold(messageData.data.player);
                            break;

                        //case 'receive_player_card':
                        //    $scope.wsController.receivePlayerCard(messageData.data.player, messageData.data.card);
                        //    break;
                        //case 'receive_board_card':
                        //    $scope.wsController.receiveBoardCard(messageData.data.card);
                        //    break;
                    }
                    break;
            }
        });

        $scope.wsController = {
            joinedTable: function(player) {
                $scope.$apply(function() {
                    $scope.players.push(player);
                    console.log('Player ' + player.name + ' joined.');
                });
            },
            leavedTable: function(player) {
                $scope.$apply(function() {
                    for (var idx in $scope.players) {
                        if ($scope.players[idx].id === player.id) {
                            $scope.players.splice(idx, 1);
                            console.log('Player ' + player.name + ' left.');
                            break;
                        }
                    }
                });
            },
            bet: function(player, amount) {
                $scope.$apply(function() {
                    $scope.circlePot += amount;
                    $scope.pot += amount;
                    console.log('Player ' + player.name + ' bet ' + amount);
                });
            },
            fold: function(player) {
                $scope.$apply(function() {
                    console.log('Player ' + player.name + ' fold.');
                });
            }//,
            //receivePlayerCard: function(player, card) {
            //    $scope.$apply(function() {
            //        console.log('Player ' + player.name + ' get ' + card + ' card.');
            //    });
            //},
            //receiveBoardCard: function(card) {
            //    $scope.$apply(function() {
            //        console.log('Board get ' + card + ' card.');
            //    });
            //}
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
    var sid = '';
    var connection = false;
    var isAuth = false;

    var wsSend = function(messageObj) {
        //messageObj['sid'] = sid;
        var sendMessage = function(msgObj) {
            var msg = JSON.stringify(msgObj);
            ws.send(msg);
        };

        if (!isAuth) {
            sendMessage({"sid": sid});
            isAuth = true;
        }
        sendMessage(messageObj);
    };

    service.connect = function() {
        ws = new SockJS(ws_url, null, ws_options);
        ws.onmessage = function (message) {
        };

        ws.onclose = function () {
            isAuth = false;
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

    service.leave = function (tableId) {
        wsSend({ type: 'table', action: 'leave', data: { table_id: tableId } });
    };

    service.bet = function(tableId, amount) {
        wsSend({ type:'table', action: 'bet', data: { table_id: tableId, amount: amount } });
    };

    service.fold = function(tableId) {
        wsSend({type: 'table', action: 'fold', data: { table_id: tableId }});
    };

    service.getMessages = function() {
        return messages;
    };

    service.setSid = function(inputSid) {
        sid = inputSid;
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