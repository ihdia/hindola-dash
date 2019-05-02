# Dashboard
The dashboard used for monitoring the backend databases is Metabase. This can be downloaded [here](https://metabase.com/start/jar.html).
The above files are related to the underlying databases present in the local server. These are the files that store all the information related to graphs,histograms,databases which are shown via the dashboard.

Currently the dashboard is running on this [link](http://10.5.0.142:56000/).

To run the dashboard,
- Logon to the server
- Goto the folder containing the above files and 'metabase.jar'
- Run the command 'java -jar metabase.jar'

But this will start the server on the default port:3000, to change port to say '56000', run the command
'export MB_JETTY_PORT=56000' before starting the dashboard. 

By default the server starts as localhost i.e., 127.0.0.1, to change that run the command
'export MB_JETTY_HOST=yourIP' before starting the dashboard.
