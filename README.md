# AS_STAGES

cp AS_STAGES/settings_base.cfg AS_STAGES/settings.py

adjust settings

ajustement selinux

semanage fcontext -a -t httpd_sys_script_exec_t /full-path-to-file/_psycopg.cpython-34m.so

restorecon -v /full-path-to-file/_psycopg.cpython-34m.so
