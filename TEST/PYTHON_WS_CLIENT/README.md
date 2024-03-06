This simple app will create a websocket connection to the PUSH NOTIFICATIOn

Requirements:
    - running push notification service running on 8889
    - python dependencies websocket-client. If not installed: pip install websocket-client
    
Running:
    - python script require two params: user(for whom we create the websocket) and the port number(use by default:8889)
    - First method: sh -x start_client.sh
    - Second method: python ws_client.py 8889 dan
  
 The client will print at stdount the job status