server {
	listen 80;
	server_name fleeter.windshieldink.loc;
	access_log /home/kostya/projects/wsi-apiv2/logs/access.log;
        error_log /home/kostya/projects/wsi-apiv2/logs/error.log;


	location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
		root /home/kostya/projects/wsi-apiv2;
	}

	location / {
		include 	uwsgi_params;
		uwsgi_pass 	unix:/home/kostya/projects/wsi-apiv2/wsi/fleeter.sock;
	}
}
