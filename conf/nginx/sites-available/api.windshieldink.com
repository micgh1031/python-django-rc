server {
	listen 80;
	server_name api.windshieldink.loc www.windshieldink.loc;
	client_max_body_size 75M;

	location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
		root /home/kostya/projects/wsi-apiv2;
	}

	location / {
		include 	uwsgi_params;
		uwsgi_pass 	unix:/home/kostya/projects/wsi-apiv2/wsi/wsi.sock;
	}
}
