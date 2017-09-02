# AS_STAGES
commande pour ignorer les changement ultérieurs de settings.py
    git update-index --assume-unchanged django_stages/settings.py
ajustement selinux
semanage fcontext -a -t httpd_sys_script_exec_t </full-path-to-file/_psycopg.cpython-34m.so‌>
restorecon -v </full-path-to-file/_psycopg.cpython-34m.so‌>
