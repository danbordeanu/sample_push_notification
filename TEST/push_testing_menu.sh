#!/bin/bash
#TODO
# 1. add full cycle test including websocket connection
# 2. handle processes by pid: and send escape sequence (like Ctrl+D) 



#do some checks
# dialog is a must, without it no magic
if ! [ -x "$(command -v dialog)" ]; then
  echo 'Error: dialog is not installed.....run aptitude install dialog' >&2
  exit 1
fi

# TODO this is killing some on my daemons!! move to PID based 
# killall used to kill services, seems is not part of base debian
if ! [ -x "$(command -v killall)" ]; then
  echo 'Error: killall is not installed.....run aptitude install psmisc' >&2
  exit 1
fi

# multitail to aggregate logs
if ! [ -x "$(command -v multitail)" ]; then
  echo 'Error: multitail is not installed.....aptitude install multitail' >&2
  exit 1
fi


# lsof to get pid of port
if ! [ -x "$(command -v lsof)" ]; then
  echo 'Error: lsof is not installed.....aptitude install lsof' >&2
  exit 1
fi

# docker-compose to spin up all containers
if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker is not installed.....Please read the docs to install docker-ce and docker-compose' >&2
  exit 1
fi



#set variables
INPUT=/tmp/menu.sh.$$
OUTPUT=/tmp/output.sh.$$

# services nane
HTTP_MOCK=http_server.py
PUSH_NOTIF=NotificationServer_QUEUE.py

# how many get requests for job id
REQUESTS=100

# interval to send requests
INTERVAL=1


# trap and delete temp files
trap "rm $OUTPUT; rm $INPUT; exit" SIGHUP SIGINT SIGTERM


# set env for local http proxy
function export_environment(){
echo 'We will set the local http proxy as env'
export HPC_APIURL='http://localhost:8081/api/v2'
}

export_environment


# start http mock
function start_http(){
if lsof -n -ti:8081 &>/dev/null; then
    dialog --title 'HTTP' --msgbox 'Seems running, consider killing it...' 5 20
else
    #nohup python http_mock.py &> output_push.log
    cd HPC_API_JOB_MOCK
    python $HTTP_MOCK &> http_out.log &
    cd ..
fi

}

# start push notitication
function start_push(){
if lsof -n -ti:8889 &>/dev/null; then
    dialog --title 'PUSH' --msgbox 'Seems running, consider killing it...' 5 20
else
    cd ../NOTIFICATIONS_QUEUE
    python $PUSH_NOTIF &> output_push.log &
    cd ../TEST
fi
cd ../TEST
}


# about 
function about_about(){
dialog --title 'ABOUT' --msgbox 'Dan is the best and he created this' 10 20
}


# killall services aka push service and http mock
function stop_all(){
dialog --title 'KILLINGALL' --msgbox 'Start killing everyone on board' 5 50
if lsof -n -ti:8889  &>/dev/null; then
    kill -9 `lsof -n -ti:8889`
else 
    echo 'notification not running'
    dialog --title 'NOKILL' --msgbox 'notification not running' 5 50
fi


if lsof -n -ti:8081 &>/dev/null; then
kill -9 `lsof -n -ti:8081`
else 
    echo 'http-server mock not running'
    dialog --title 'NOKILL' --msgbox 'http server not running' 5 50
fi
}

# send get job status for user DAN
function getstatusfirst(){
dialog --title 'GET JOB FIRST' --msgbox 'Get 100 job status for user dan' 5 50
echo 'Sending:'$REQUESTS' at '$INTERVAL' interval'

for ((i=1;i<=$REQUESTS;i++)); 
do
   echo -e '\n'
   echo -e 'Sending request number '$i''
   curl 'http://localhost:8887/push?userid=dan&ticket=ST-2157-j6WQCu4OtqiX95vOlEqZ-bla-dev.host.com&jobid='$i''
   sleep $INTERVAL
done
}


# create websicket for user DAN
function makesocketfirst(){
#detect env
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to make websocket' 5 60
cd PYTHON_WS_CLIENT
xfce4-terminal --command='python ws_client.py 8887 dan' &
cd ..
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you? Making a socket for you' 5 60
cd PYTHON_WS_CLIENT
gnome-terminal -e 'python ws_client.py 8887 dan'  &
cd ..
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 40
cd PYTHON_WS_CLIENT
xterm -e 'python ws_client.py 8887 dan' &
cd ..
;;
esac
}

# create websicket for user ALEX
function makesocketsecond(){
#detect env
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to make websocket' 5 60
cd PYTHON_WS_CLIENT
xfce4-terminal --command='python ws_client.py 8887 alex' &
cd ..
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you? Making a socket for you' 5 60
gnome-terminal -e 'python ws_client.py 8887 alex'  &
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 40
xterm -e 'python ws_client.py 8887 alex' &
;;
esac

}

# send get job status for user ALEX
function getstatussecond(){
dialog --title 'GET JOB SECOND' --msgbox 'Get 100 job status for user alex' 5 50
echo 'Sending:'$REQUESTS' at '$INTERVAL' interval'
for ((i=1;i<=$REQUESTS;i++)); 
do
   echo -e '\n'
   echo -e 'Sending request number '$i''
   curl  'http://localhost:8887/push?userid=alex&ticket=ST-2157-j6WQCu4OtqiX95vOlEqZ-bla-dev.host.com&jobid='$i''
   sleep $INTERVAL
done
}

# send get job status for two users in the same time
function flooding()
{
dialog --title 'FLOODIND' --msgbox 'Get 100 job status for user two users' 5 50
echo 'Sending:'$REQUESTS' at '$INTERVAL' interval for two users'
for ((i=1;i<=$REQUESTS;i++)); 
do
   echo -e '\n'
   echo -e 'Sending request number '$i''
   curl 'http://localhost:8887/push?userid=dan&ticket=ST-2157-j6WQCu4OtqiX95vOlEqZ-bla-dev.host.com&jobid='$i''
   curl 'http://localhost:8887/push?userid=alex&ticket=ST-2157-j6WQCu4OtqiX95vOlEqZ-bla-dev.host.com&jobid='$i''
   sleep $INTERVAL
done
}


# start mock/push/socket in the same time

function start_all()
{
dialog --title 'STARTALL' --msgbox 'Start mock/push/socket' 5 50
start_http
start_push
sleep 5
makesocketfirst
}

# spinning up all docker containers:rabbit, memcached, push, nginx and pushnotification

function docker_start()
{
dialog --title 'DOCKER' --msgbox 'WARNING,starting all docker containers' 5 60
docker-compose -f ../DOCKER/X64/docker-compose-mock.yml up -d
}

# switching off all docker containers

function docker_stop()
{
dialog --title 'DOCKER' --msgbox 'WARNING, shutting down all docker containers' 5 60
docker-compose -f ../DOCKER/X64/docker-compose-mock.yml down
}



# exit program and clean up variables
function exit_all(){
unset HPC_APIURL
[ -f $OUTPUT ] && rm $OUTPUT
[ -f $INPUT ] && rm $INPUT
exit
}


function logs_aggregator()
{
#detect env
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to aggregate logs' 5 60
xfce4-terminal --command='multitail -ci red HPC_API_JOB_MOCK/http_out.log -ci yellow ../NOTIFICATIONS_QUEUE/output_push.log'  &
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you?' 5 20
gnome-terminal -e 'multitail -ci red HPC_API_JOB_MOCK/http_out.log -ci yellow ../NOTIFICATIONS_QUEUE/output_push.log'  &
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 20
xterm -e 'multitail -ci red HPC_API_JOB_MOCK/http_out.log -ci yellow ../NOTIFICATIONS_QUEUE/output_push.log' &
;;
esac
}

function docker_logs()
{
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to aggregate docker logs' 5 60
xfce4-terminal --command='docker-compose -f ../DOCKER/X64/docker-compose-mock.yml logs --tail=0 --follow'  &
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you?' 5 20
gnome-terminal -e 'docker-compose -f ../DOCKER/X64/docker-compose-mock.yml logs --tail=0 --follow'  &
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 20
xterm -e 'docker-compose -f ../DOCKER/X64/docker-compose-mock.yml logs --tail=0 --follow' &
;;
esac
}
# making the forever and after loop
while true
do


# creating the menus
dialog --clear --backtitle "PUSH NOTIFICATION" \
--title "[ ACTION - ACTION ]" \
--menu "You can use the UP/DOWN arrow keys to choose the TASK" 20 100 60 \
STARTALL "Start mock/push/socket in the same time" \
HPCAPI_MOCK "Start http mock instead of calling hpcapi" \
NotificationServer_QUEUE "Start the notification server" \
KILLALL "Kill all daemons" \
GETSTATUS-A "Get Job status for user DAN" \
GETSTATUS-B "Get Job status for user ALEX" \
SOCKET-A "Make socket for user DAN" \
SOCKET-B "Make socket for user ALEX" \
LOGS "Get logs for http and notification services" \
FLOOD "Get Job status for two users" \
DOCKER-UP "Start docker compose" \
DOCKER-DOWN "Shutting down docker compose" \
DOCKER-LOGS "Get logs from docker containers" \
ABOUT "About" \
Exit "Exit to the shell" 2>"${INPUT}"


menuitem=$(<"${INPUT}")

# make decision, we love case
case $menuitem in
STARTALL) start_all;;
HPCAPI_MOCK) start_http;;
NotificationServer_QUEUE) start_push;;
KILLALL) stop_all;;
GETSTATUS-A) getstatusfirst;;
GETSTATUS-B) getstatussecond;;
SOCKET-A) makesocketfirst;;
SOCKET-B) makesocketsecond;;
LOGS) logs_aggregator;;
DOCKER-LOGS) docker_logs;;
FLOOD) flooding;;
DOCKER-UP) docker_start;;
DOCKER-DOWN) docker_stop;;
ABOUT) about_about;;
Exit) exit_all;;
esac

done



