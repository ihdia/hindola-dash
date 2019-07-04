# Dashboard
The dashboard used for monitoring the backend databases is Metabase. This can be downloaded [here](https://metabase.com/start/jar.html).
The above files are related to the underlying databases present in the local server. These are the files that store all the information related to graphs,histograms,databases of the application which you are running,and are shown on the dashboard.

To run Metabase, you will need to have Java8 or above installed in your system. 

For more information on setting up Metabse refer to this https://metabase.com/docs/latest/

To run the dashboard,
- Logon to the server
- Goto the folder containing the database files of your application and save 'metabase.jar' in the same folder. 
- Run the command 'java -jar metabase.jar' in Command prompt(Windows) or Terminal(linux or Mac).

But this will start the server on the default port:3000, to change port to say '56000', run the command
'export MB_JETTY_PORT=56000' before starting the dashboard. 

By default the server starts as localhost i.e., 127.0.0.1, to change that run the command
'export MB_JETTY_HOST=yourIP' before starting the dashboard.

# Viewer
This is the site for viewing the Annotated, the Unannotated and the Bookmarked images.

The instructions for setting up the viewer are provided in the link https://github.com/ihdia/hindola-dash/tree/master/Viewer_1-master

### Videos
Dashboard -  https://tinyurl.com/hindola-v1-dashbrd
